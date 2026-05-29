import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:drift/drift.dart' hide Column;
import 'package:http/http.dart' as http;

import '../core/app_config.dart';
import '../database/app_database.dart';
import '../dropdown/dropdown_service.dart';
import 'sync_status_event.dart';

const _kDefaultBaseUrl = AppConfig.backendBaseUrl;
const _kBatchSize = 50;

/// Manages offline-to-server synchronisation.
///
/// - Reads `sync_queue WHERE status='pending' LIMIT 50`
/// - Marks records `in_flight`
/// - POSTs multipart payload to `POST /api/v1/sync/upload`
/// - Updates `sync_status` on parent street/building rows
/// - Writes to device `audit_log`
/// - Emits [SyncStatusEvent]s on [statusStream]
///
/// Requirements: 7.1, 7.3, 7.4, 7.5, 7.6
class SyncEngine {
  final AppDatabase db;
  final http.Client _client;

  final _statusController =
      StreamController<SyncStatusEvent>.broadcast();

  /// Broadcast stream of sync progress events for the UI.
  Stream<SyncStatusEvent> get statusStream => _statusController.stream;

  SyncEngine({
    required this.db,
    http.Client? client,
  })  : _client = client ?? http.Client();

  // ─── Workmanager registration ─────────────────────────────────────────────

  /// Registers the periodic background sync task with Workmanager.
  ///
  /// Call once from [main] after [WidgetsFlutterBinding.ensureInitialized].
  /// 
  /// NOTE: Currently disabled due to plugin initialization issues.
  /// Background sync will be re-enabled in a future update.
  static Future<void> registerBackgroundTask() async {
    // TODO: Re-enable workmanager once plugin issues are resolved
    // For now, sync only happens when manually triggered from UI
    return;
  }

  // ─── Manual trigger ───────────────────────────────────────────────────────

  /// Triggers an immediate sync cycle (called from the UI).
  Future<void> triggerManualSync() => runSyncCycle();

  // ─── Core sync cycle ──────────────────────────────────────────────────────

  /// Runs one full sync cycle: fetch pending → upload → update statuses.
  Future<void> runSyncCycle() async {
    // Get access token from database session, refreshing if expired.
    final token = await _getValidToken();
    if (token == null) {
      _emit(SyncFailed('No active session — please log in'));
      return;
    }

    // 1. Fetch pending items.
    final pending = await (db.select(db.syncQueue)
          ..where((t) => t.status.equals('pending'))
          ..orderBy([(t) => OrderingTerm.asc(t.createdAt)])
          ..limit(_kBatchSize))
        .get();

    if (pending.isEmpty) return;

    _emit(SyncStarted(pending.length));

    // 2. Mark all as in_flight.
    final ids = pending.map((r) => r.id).toList();
    await (db.update(db.syncQueue)
          ..where((t) => t.id.isIn(ids)))
        .write(SyncQueueCompanion(
      status: const Value('in_flight'),
      lastAttemptAt: Value(DateTime.now().millisecondsSinceEpoch),
    ));

    // 3. Build and POST the multipart payload.
    final uri = Uri.parse('$_kDefaultBaseUrl/api/v1/sync/upload');

    int accepted = 0;
    int rejected = 0;

    try {
      final request = http.MultipartRequest('POST', uri)
        ..headers['Authorization'] = 'Bearer $token';

      // Attach records JSON — wrap each item as {entity_type, local_id, data}.
      // Include photo metadata entries so backend can link photos to records.
      final recordsJson = jsonEncode(
        pending
            .map((r) {
              final payload = jsonDecode(r.payloadJson) as Map<String, dynamic>;
              if (r.entityType == 'photo') {
                // Send photo metadata (without file_path) in records_json.
                final meta = Map<String, dynamic>.from(payload)
                  ..remove('file_path');
                return {
                  'entity_type': 'photo',
                  'local_id': r.entityLocalId,
                  'data': meta,
                };
              }
              return {
                'entity_type': r.entityType,
                'local_id': r.entityLocalId,
                'data': payload,
              };
            })
            .toList(),
      );
      request.fields['records_json'] = recordsJson;
      request.fields['device_id'] = await _getDeviceId();

      // Attach photo files for photo-type queue entries.
      for (final item in pending.where((r) => r.entityType == 'photo')) {
        final payload =
            jsonDecode(item.payloadJson) as Map<String, dynamic>;
        final filePath = payload['file_path'] as String?;
        if (filePath != null) {
          final file = File(filePath);
          if (file.existsSync()) {
            request.files.add(await http.MultipartFile.fromPath(
              'photos',
              file.path,
            ));
          }
        }
      }

      final streamed = await _client.send(request).timeout(
        const Duration(seconds: 120),
        onTimeout: () => throw Exception('Sync upload timed out after 120 seconds'),
      );
      final response = await http.Response.fromStream(streamed);

      if (response.statusCode == 200) {
        final body =
            jsonDecode(response.body) as Map<String, dynamic>;
        final results =
            (body['results'] as List<dynamic>? ?? [])
                .cast<Map<String, dynamic>>();

        for (final result in results) {
          final localId = result['local_id'] as int?;
          final status = result['status'] as String?;
          final serverId = result['server_id'] as String?;
          final errors = (result['errors'] as List<dynamic>? ?? [])
              .cast<String>();
          final entityType = result['entity_type'] as String? ?? '';

          if (localId == null) continue;

          if (status == 'accepted' && serverId != null) {
            await _markAccepted(localId, entityType, serverId);
            _emit(SyncRecordAccepted(
                localId: localId,
                entityType: entityType,
                serverId: serverId));
            accepted++;
          } else {
            final errorMsg = errors.join('; ');
            await _markFailed(localId, errorMsg);
            _emit(SyncRecordRejected(
                localId: localId,
                entityType: entityType,
                errors: errors));
            rejected++;
          }
        }
      } else {
        // Server error — revert all to pending for retry.
        await _revertToRetry(ids, 'HTTP ${response.statusCode}');
        final msg = response.statusCode == 401
            ? 'Session expired — please log in again'
            : 'Server error: ${response.statusCode}';
        _emit(SyncFailed(msg));
        return;
      }
    } catch (e) {
      await _revertToRetry(ids, e.toString());
      _emit(SyncFailed('Network error: $e'));
      return;
    }

    // 4. Write sync operation to audit_log.
    await _writeAuditLog(accepted, rejected);

    // 5. Refresh dropdown config from server (best-effort, non-blocking).
    final dropdownService = DropdownService(db: db);
    await dropdownService.syncFromServer();

    _emit(SyncCompleted(accepted: accepted, rejected: rejected));
  }

  // ─── Status update helpers ────────────────────────────────────────────────

  /// Returns a valid access token, refreshing it if expired.
  /// Returns null if no session exists or refresh fails.
  Future<String?> _getValidToken() async {
    final sessionRows = await db.select(db.sessions).get();
    if (sessionRows.isEmpty) return null;

    final session = sessionRows.first;
    final now = DateTime.now().millisecondsSinceEpoch;

    // If token expires in more than 60 seconds, use it as-is.
    if (session.tokenExpiresAt > now + 60000) {
      return session.accessToken;
    }

    // Token expired or about to expire — try to refresh.
    try {
      final uri = Uri.parse('$_kDefaultBaseUrl/api/v1/auth/refresh');
      final response = await _client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: '{"refresh_token":"${session.refreshToken}"}',
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        final newAccessToken = body['access_token'] as String;
        final newRefreshToken = body['refresh_token'] as String? ?? session.refreshToken;
        final expiresIn = (body['expires_in'] as num?)?.toInt() ?? 28800;
        final newExpiresAt = now + expiresIn * 1000;

        // Update session in DB.
        await (db.update(db.sessions)
              ..where((t) => t.userId.equals(session.userId)))
            .write(SessionsCompanion(
          accessToken: Value(newAccessToken),
          refreshToken: Value(newRefreshToken),
          tokenExpiresAt: Value(newExpiresAt),
        ));

        return newAccessToken;
      } else {
        // Refresh failed — clear session so user is prompted to log in.
        await (db.delete(db.sessions)).go();
        return null;
      }
    } catch (_) {
      // Network error during refresh — use the old token and let the server
      // return 401 if it's truly expired.
      return session.accessToken;
    }
  }

  Future<void> _markAccepted(
      int entityLocalId, String entityType, String serverId) async {
    // Update sync_queue row by entityLocalId.
    await (db.update(db.syncQueue)
          ..where((t) => t.entityLocalId.equals(entityLocalId)
              & t.entityType.equals(entityType)))
        .write(const SyncQueueCompanion(status: Value('done')));

    // Update parent entity sync_status + server_id.
    if (entityType == 'street') {
      await (db.update(db.streets)
            ..where((t) => t.id.equals(entityLocalId)))
          .write(StreetsCompanion(
        syncStatus: const Value('synced'),
        serverId: Value(serverId),
      ));
    } else if (entityType == 'building') {
      await (db.update(db.buildings)
            ..where((t) => t.id.equals(entityLocalId)))
          .write(BuildingsCompanion(
        syncStatus: const Value('synced'),
        serverId: Value(serverId),
      ));
    } else if (entityType == 'photo') {
      await (db.update(db.photos)
            ..where((t) => t.id.equals(entityLocalId)))
          .write(const PhotosCompanion(
        syncStatus: Value('synced'),
      ));
    }
  }

  Future<void> _markFailed(int entityLocalId, String error) async {
    await (db.update(db.syncQueue)
          ..where((t) => t.entityLocalId.equals(entityLocalId)))
        .write(SyncQueueCompanion(
      status: const Value('failed'),
      lastError: Value(error),
    ));
  }

  Future<void> _revertToRetry(List<int> ids, String error) async {
    await (db.update(db.syncQueue)
          ..where((t) => t.id.isIn(ids)))
        .write(SyncQueueCompanion(
      status: const Value('pending'),
      lastError: Value(error),
      attemptCount: const Value(0), // will be incremented on next attempt
    ));
  }

  Future<void> _writeAuditLog(int accepted, int rejected) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    await db.into(db.auditLog).insert(AuditLogCompanion.insert(
          operation: 'sync_upload',
          entityType: Value('sync_session'),
          entityId: Value('batch_$now'),
          userId: 'system',
          detailJson: Value(jsonEncode({
            'accepted': accepted,
            'rejected': rejected,
            'timestamp': now,
          })),
          occurredAt: Value(now),
        ));
  }

  void _emit(SyncStatusEvent event) {
    if (!_statusController.isClosed) {
      _statusController.add(event);
    }
  }

  /// Returns a device ID stored in the local SQLite DB.
  ///
  /// Storing in SQLite (not flutter_secure_storage) means the ID is wiped
  /// when the user clears app data. This is intentional: after a data clear,
  /// a new device_id is generated so the backend can detect ID collisions
  /// (same street_id from a different "session") and create distinct records
  /// with a suffix rather than silently returning the old record.
  Future<String> _getDeviceId() async {
    const key = 'device_id';
    final row = await (db.select(db.deviceSettings)
          ..where((t) => t.key.equals(key)))
        .getSingleOrNull();
    if (row != null && row.value.isNotEmpty) return row.value;

    // Generate a random 16-byte hex ID.
    final rng = Random.secure();
    final bytes = List<int>.generate(16, (_) => rng.nextInt(256));
    final id = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();

    await db.into(db.deviceSettings).insert(
          DeviceSettingsCompanion.insert(key: key, value: id),
          mode: InsertMode.insertOrReplace,
        );
    return id;
  }

  Future<void> dispose() async {
    await _statusController.close();
    _client.close();
  }
}
