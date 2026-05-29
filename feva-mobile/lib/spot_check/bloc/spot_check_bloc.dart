import 'dart:convert';

import 'package:drift/drift.dart' hide Column;
import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;

import '../../database/app_database.dart';

part 'spot_check_event.dart';
part 'spot_check_state.dart';

/// Unified record for the spot-check list — wraps either a Building or Street.
class SpotCheckRecord extends Equatable {
  final String entityType; // 'building' | 'street'
  final int localId;
  final String recordId; // building_id or street_id
  final String lga;
  final String? ward;
  final String enumeratorId;
  final int enumerationDate; // Unix epoch ms
  final String verificationStatus;

  const SpotCheckRecord({
    required this.entityType,
    required this.localId,
    required this.recordId,
    required this.lga,
    this.ward,
    required this.enumeratorId,
    required this.enumerationDate,
    required this.verificationStatus,
  });

  @override
  List<Object?> get props => [entityType, localId, recordId];
}

/// Manages supervisor spot-check list and approve/reject actions.
///
/// Requirements: 12.1–12.5
class SpotCheckBloc extends Bloc<SpotCheckEvent, SpotCheckState> {
  final AppDatabase db;
  final http.Client httpClient;
  final String baseUrl;
  final String accessToken;

  /// The supervisor's user ID (written to audit_log).
  final String supervisorId;

  /// The LGA code assigned to this supervisor.
  final String assignedLga;

  SpotCheckBloc({
    required this.db,
    required this.httpClient,
    required this.baseUrl,
    required this.accessToken,
    required this.assignedLga,
    required this.supervisorId,
  }) : super(const SpotCheckInitial()) {
    on<LoadSpotCheckRecords>(_onLoad);
    on<ApproveRecord>(_onApprove);
    on<RejectRecord>(_onReject);
  }

  // ─── Load ──────────────────────────────────────────────────────────────────

  Future<void> _onLoad(
      LoadSpotCheckRecords event, Emitter<SpotCheckState> emit) async {
    emit(const SpotCheckLoading());
    try {
      final records = <SpotCheckRecord>[];

      // Buildings in assigned LGA, sorted by enumerationDate desc
      final buildings = await (db.select(db.buildings)
            ..where((t) => t.lga.equals(assignedLga))
            ..orderBy([(t) => OrderingTerm.desc(t.enumerationDate)]))
          .get();

      for (final b in buildings) {
        records.add(SpotCheckRecord(
          entityType: 'building',
          localId: b.id,
          recordId: b.buildingId,
          lga: b.lga,
          ward: b.ward,
          enumeratorId: b.enumeratorId,
          enumerationDate: b.enumerationDate,
          verificationStatus: b.verificationStatus ?? 'pending',
        ));
      }

      // Streets in assigned LGA, sorted by enumerationDate desc
      final streets = await (db.select(db.streets)
            ..where((t) => t.lga.equals(assignedLga))
            ..orderBy([(t) => OrderingTerm.desc(t.enumerationDate)]))
          .get();

      for (final s in streets) {
        records.add(SpotCheckRecord(
          entityType: 'street',
          localId: s.id,
          recordId: s.streetId,
          lga: s.lga,
          ward: s.ward,
          enumeratorId: s.enumeratorId,
          enumerationDate: s.enumerationDate,
          verificationStatus: s.verificationStatus ?? 'pending',
        ));
      }

      // Sort combined list by enumerationDate desc
      records.sort((a, b) => b.enumerationDate.compareTo(a.enumerationDate));

      emit(SpotCheckLoaded(records));
    } catch (e) {
      emit(SpotCheckError('Failed to load records: $e'));
    }
  }

  // ─── Approve ───────────────────────────────────────────────────────────────

  Future<void> _onApprove(
      ApproveRecord event, Emitter<SpotCheckState> emit) async {
    emit(const SpotCheckSubmitting());
    try {
      final now = DateTime.now().millisecondsSinceEpoch;

      // PATCH server
      await _patchVerification(
        entityType: event.entityType,
        serverId: event.serverId,
        status: 'approved',
      );

      // Update local DB
      if (event.entityType == 'building') {
        await (db.update(db.buildings)
              ..where((t) => t.id.equals(event.localId)))
            .write(BuildingsCompanion(
          verificationStatus: const Value('approved'),
          lastModifiedAt: Value(now),
        ));
      } else {
        await (db.update(db.streets)
              ..where((t) => t.id.equals(event.localId)))
            .write(StreetsCompanion(
          verificationStatus: const Value('approved'),
          lastModifiedAt: Value(now),
        ));
      }

      // Write to audit_log
      await _writeAuditLog(
        operation: 'approve',
        entityType: event.entityType,
        entityLocalId: event.localId,
        now: now,
      );

      emit(SpotCheckActionSuccess('approved'));
      add(const LoadSpotCheckRecords());
    } catch (e) {
      emit(SpotCheckError('Failed to approve: $e'));
    }
  }

  // ─── Reject ────────────────────────────────────────────────────────────────

  Future<void> _onReject(
      RejectRecord event, Emitter<SpotCheckState> emit) async {
    if (event.rejectionReason.trim().isEmpty) {
      emit(const SpotCheckError('Rejection reason is required.'));
      return;
    }

    emit(const SpotCheckSubmitting());
    try {
      final now = DateTime.now().millisecondsSinceEpoch;

      // PATCH server
      await _patchVerification(
        entityType: event.entityType,
        serverId: event.serverId,
        status: 'rejected',
        rejectionReason: event.rejectionReason,
      );

      // Update local DB
      if (event.entityType == 'building') {
        await (db.update(db.buildings)
              ..where((t) => t.id.equals(event.localId)))
            .write(BuildingsCompanion(
          verificationStatus: const Value('rejected'),
          rejectionReason: Value(event.rejectionReason),
          lastModifiedAt: Value(now),
        ));
      } else {
        await (db.update(db.streets)
              ..where((t) => t.id.equals(event.localId)))
            .write(StreetsCompanion(
          verificationStatus: const Value('rejected'),
          lastModifiedAt: Value(now),
        ));
      }
      await _writeAuditLog(
        operation: 'reject',
        entityType: event.entityType,
        entityLocalId: event.localId,
        now: now,
        detail: event.rejectionReason,
      );

      emit(SpotCheckActionSuccess('rejected'));
      add(const LoadSpotCheckRecords());
    } catch (e) {
      emit(SpotCheckError('Failed to reject: $e'));
    }
  }

  // ─── Helpers ───────────────────────────────────────────────────────────────

  Future<void> _patchVerification({
    required String entityType,
    required String? serverId,
    required String status,
    String? rejectionReason,
  }) async {
    if (serverId == null) return; // Not yet synced — local-only update
    final uri =
        Uri.parse('$baseUrl/api/v1/records/${entityType}s/$serverId');
    final body = <String, dynamic>{'verification_status': status};
    if (rejectionReason != null) body['rejection_reason'] = rejectionReason;

    final response = await httpClient.patch(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
      body: jsonEncode(body),
    );

    if (response.statusCode != 200) {
      throw Exception(
          'Server returned ${response.statusCode}: ${response.body}');
    }
  }

  Future<void> _writeAuditLog({
    required String operation,
    required String entityType,
    required int entityLocalId,
    required int now,
    String? detail,
  }) async {
    await db.into(db.auditLog).insert(AuditLogCompanion.insert(
          userId: supervisorId,
          operation: operation,
          entityType: Value(entityType),
          entityId: Value(entityLocalId.toString()),
          detailJson: Value(detail),
          occurredAt: Value(now),
        ));
  }
}
