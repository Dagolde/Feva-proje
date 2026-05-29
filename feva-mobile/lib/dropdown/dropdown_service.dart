import 'dart:convert';

import 'package:drift/drift.dart' hide Column;
import 'package:http/http.dart' as http;

import '../core/app_config.dart';
import '../database/app_database.dart';

/// A single dropdown option.
class DropdownOption {
  final String value;
  final String label;
  final int sortOrder;

  const DropdownOption({
    required this.value,
    required this.label,
    required this.sortOrder,
  });
}

/// Provides configurable dropdown values for capture forms.
///
/// Values are read from the local [AppDatabase] `dropdown_config` table.
/// On sync, the latest config is downloaded from [GET /api/v1/sync/config]
/// and upserted into the local table.
///
/// Falls back to the last downloaded config when offline.
///
/// Requirements: 18.1, 18.2, 18.3, 18.4
class DropdownService {
  final AppDatabase db;
  final http.Client _client;

  DropdownService({
    required this.db,
    http.Client? client,
  })  : _client = client ?? http.Client();

  // ─── Read from local DB ───────────────────────────────────────────────────

  /// Returns all options for [category], sorted by [sortOrder].
  ///
  /// Categories: 'street_type', 'surface_type', 'street_condition',
  ///             'building_type', 'building_condition'
  Future<List<DropdownOption>> getOptions(String category) async {
    final rows = await (db.select(db.dropdownConfig)
          ..where((t) => t.category.equals(category))
          ..orderBy([(t) => OrderingTerm.asc(t.sortOrder)]))
        .get();

    return rows
        .map((r) => DropdownOption(
              value: r.value,
              label: r.label,
              sortOrder: r.sortOrder,
            ))
        .toList();
  }

  /// Convenience getters for each category used in capture forms.
  Future<List<DropdownOption>> get streetTypes => getOptions('street_type');
  Future<List<DropdownOption>> get surfaceTypes => getOptions('surface_type');
  Future<List<DropdownOption>> get streetConditions =>
      getOptions('street_condition');
  Future<List<DropdownOption>> get buildingTypes => getOptions('building_type');
  Future<List<DropdownOption>> get buildingConditions =>
      getOptions('building_condition');

  // ─── Sync from server ─────────────────────────────────────────────────────

  /// Downloads the latest dropdown config from the server and upserts into
  /// the local [dropdown_config] table.
  ///
  /// Returns `true` on success, `false` on network/server failure.
  /// Failures are logged to the device [audit_log] with a timestamp.
  Future<bool> syncFromServer() async {
    // Get access token from database session
    final sessionRows = await db.select(db.sessions).get();
    if (sessionRows.isEmpty) return false;
    
    final token = sessionRows.first.accessToken;
    final uri = Uri.parse('${AppConfig.backendBaseUrl}/api/v1/sync/config');

    try {
      final response = await _client.get(
        uri,
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode != 200) {
        await _logFailure(
            'config_sync_failed', 'HTTP ${response.statusCode}');
        return false;
      }

      final body = jsonDecode(response.body) as Map<String, dynamic>;
      final configMap =
          (body['dropdown_config'] as Map<String, dynamic>? ?? {});

      await _upsertConfig(configMap);

      return true;
    } catch (e) {
      await _logFailure('config_sync_error', e.toString());
      return false;
    }
  }

  // ─── Upsert helpers ───────────────────────────────────────────────────────

  Future<void> _upsertConfig(Map<String, dynamic> configMap) async {
    final now = DateTime.now().millisecondsSinceEpoch;

    for (final entry in configMap.entries) {
      final category = entry.key;
      final items = (entry.value as List<dynamic>).cast<Map<String, dynamic>>();

      for (final item in items) {
        final value = item['value'] as String? ?? '';
        final label = item['label'] as String? ?? value;
        final sortOrder = (item['sort_order'] as num?)?.toInt() ?? 0;
        final version = (item['version'] as num?)?.toInt() ?? 1;

        // Upsert: insert or replace on (category, value) conflict.
        await db.into(db.dropdownConfig).insertOnConflictUpdate(
              DropdownConfigCompanion.insert(
                category: category,
                value: value,
                label: label,
                sortOrder: Value(sortOrder),
                version: Value(version),
                syncedAt: Value(now),
              ),
            );
      }
    }
  }

  Future<void> _logFailure(String operation, String detail) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    await db.into(db.auditLog).insert(AuditLogCompanion.insert(
          operation: operation,
          entityType: Value('dropdown_config'),
          entityId: Value('sync'),
          userId: 'system',
          detailJson: Value(jsonEncode({
            'error': detail,
            'timestamp': now,
          })),
          occurredAt: Value(now),
        ));
  }
}
