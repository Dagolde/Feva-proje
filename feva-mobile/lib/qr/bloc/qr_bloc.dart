import 'dart:convert';

import 'package:drift/drift.dart' hide Column;
import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;

import '../../database/app_database.dart';

part 'qr_event.dart';
part 'qr_state.dart';

/// Manages QR code scanning and building verification/dispute.
///
/// Requirements: 17.1–17.5, 17.7
class QrBloc extends Bloc<QrEvent, QrState> {
  final AppDatabase db;
  final http.Client httpClient;
  final String baseUrl;
  final String accessToken;
  final String supervisorId;

  QrBloc({
    required this.db,
    required this.httpClient,
    required this.baseUrl,
    required this.accessToken,
    required this.supervisorId,
  }) : super(const QrInitial()) {
    on<ScanQrCode>(_onScan);
    on<VerifyBuilding>(_onVerify);
    on<DisputeBuilding>(_onDispute);
    on<VerifyStreet>(_onVerifyStreet);
    on<DisputeStreet>(_onDisputeStreet);
  }

  Future<void> _onScan(ScanQrCode event, Emitter<QrState> emit) async {
    emit(const QrLoading());
    final scannedId = event.qrValue.trim();
    if (scannedId.isEmpty) {
      emit(const QrNotFound('Empty QR code'));
      return;
    }

    try {
      // 1. Try local building DB
      final localBuilding = await (db.select(db.buildings)
            ..where((t) => t.buildingId.equals(scannedId)))
          .getSingleOrNull();

      if (localBuilding != null) {
        emit(QrBuildingFound(localBuilding));
        return;
      }

      // 2. Try local street DB
      final localStreet = await (db.select(db.streets)
            ..where((t) => t.streetId.equals(scannedId)))
          .getSingleOrNull();

      if (localStreet != null) {
        emit(QrStreetFound(localStreet));
        return;
      }

      // 3. Try server — building first
      final buildingUri = Uri.parse('$baseUrl/api/v1/records/buildings/$scannedId');
      final buildingResponse = await httpClient.get(buildingUri, headers: {
        'Authorization': 'Bearer $accessToken',
      });

      if (buildingResponse.statusCode == 200) {
        final data = jsonDecode(buildingResponse.body) as Map<String, dynamic>;
        emit(QrBuildingFoundRemote(data));
        return;
      }

      // 4. Try server — street fallback
      final streetUri = Uri.parse('$baseUrl/api/v1/records/streets/$scannedId');
      final streetResponse = await httpClient.get(streetUri, headers: {
        'Authorization': 'Bearer $accessToken',
      });

      if (streetResponse.statusCode == 200) {
        final data = jsonDecode(streetResponse.body) as Map<String, dynamic>;
        emit(QrStreetFoundRemote(data));
        return;
      }

      // 5. Not found anywhere
      await _writeAuditLog('qr_scan_not_found', scannedId, entityType: 'unknown');
      emit(QrNotFound('No record found for QR code: $scannedId'));
    } catch (e) {
      emit(QrError('Scan failed: $e'));
    }
  }

  Future<void> _onVerify(VerifyBuilding event, Emitter<QrState> emit) async {
    emit(const QrSubmitting());
    try {
      final now = DateTime.now().millisecondsSinceEpoch;

      // PATCH server
      await _patchVerification(
        buildingId: event.buildingId,
        status: 'verified',
        verifiedBy: supervisorId,
      );

      // Update local DB if present
      await (db.update(db.buildings)
            ..where((t) => t.buildingId.equals(event.buildingId)))
          .write(BuildingsCompanion(
        verificationStatus: const Value('verified'),
        verifiedBy: Value(supervisorId),
        verifiedAt: Value(now),
        lastModifiedAt: Value(now),
      ));

      await _writeAuditLog('verify_building', event.buildingId);
      emit(const QrActionSuccess('verified'));
    } catch (e) {
      emit(QrError('Verification failed: $e'));
    }
  }

  Future<void> _onDispute(DisputeBuilding event, Emitter<QrState> emit) async {
    if (event.disputeReason.trim().isEmpty) {
      emit(const QrError('Dispute reason is required.'));
      return;
    }
    emit(const QrSubmitting());
    try {
      final now = DateTime.now().millisecondsSinceEpoch;

      await _patchVerification(
        buildingId: event.buildingId,
        status: 'disputed',
        disputeReason: event.disputeReason,
      );

      await (db.update(db.buildings)
            ..where((t) => t.buildingId.equals(event.buildingId)))
          .write(BuildingsCompanion(
        verificationStatus: const Value('disputed'),
        disputeReason: Value(event.disputeReason),
        lastModifiedAt: Value(now),
      ));

      await _writeAuditLog('dispute_building', event.buildingId,
          detail: event.disputeReason);
      emit(const QrActionSuccess('disputed'));
    } catch (e) {
      emit(QrError('Dispute failed: $e'));
    }
  }

  Future<void> _patchVerification({
    required String buildingId,
    required String status,
    String? verifiedBy,
    String? disputeReason,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/records/buildings/$buildingId');
    final body = <String, dynamic>{'verification_status': status};
    if (verifiedBy != null) body['verified_by'] = verifiedBy;
    if (disputeReason != null) body['dispute_reason'] = disputeReason;

    final response = await httpClient.patch(uri,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode(body));

    if (response.statusCode != 200) {
      throw Exception('Server error ${response.statusCode}: ${response.body}');
    }
  }

  Future<void> _writeAuditLog(String operation, String entityId,
      {String? detail, String entityType = 'building'}) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    await db.into(db.auditLog).insert(AuditLogCompanion.insert(
          userId: supervisorId,
          operation: operation,
          entityType: Value(entityType),
          entityId: Value(entityId),
          detailJson: Value(detail),
          occurredAt: Value(now),
        ));
  }

  Future<void> _onVerifyStreet(VerifyStreet event, Emitter<QrState> emit) async {
    emit(const QrSubmitting());
    try {
      final now = DateTime.now().millisecondsSinceEpoch;

      final uri = Uri.parse('$baseUrl/api/v1/records/streets/${event.streetId}');
      final response = await httpClient.patch(uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $accessToken',
          },
          body: jsonEncode({'verification_status': 'verified'}));

      if (response.statusCode != 200) {
        throw Exception('Server error ${response.statusCode}: ${response.body}');
      }

      await (db.update(db.streets)
            ..where((t) => t.streetId.equals(event.streetId)))
          .write(StreetsCompanion(
        verificationStatus: const Value('verified'),
        lastModifiedAt: Value(now),
      ));

      await _writeAuditLog('verify_street', event.streetId, entityType: 'street');
      emit(const QrActionSuccess('verified'));
    } catch (e) {
      emit(QrError('Verification failed: $e'));
    }
  }

  Future<void> _onDisputeStreet(DisputeStreet event, Emitter<QrState> emit) async {
    if (event.disputeReason.trim().isEmpty) {
      emit(const QrError('Dispute reason is required.'));
      return;
    }
    emit(const QrSubmitting());
    try {
      final now = DateTime.now().millisecondsSinceEpoch;

      final uri = Uri.parse('$baseUrl/api/v1/records/streets/${event.streetId}');
      final response = await httpClient.patch(uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $accessToken',
          },
          body: jsonEncode({
            'verification_status': 'disputed',
            'dispute_reason': event.disputeReason,
          }));

      if (response.statusCode != 200) {
        throw Exception('Server error ${response.statusCode}: ${response.body}');
      }

      await (db.update(db.streets)
            ..where((t) => t.streetId.equals(event.streetId)))
          .write(StreetsCompanion(
        verificationStatus: const Value('disputed'),
        lastModifiedAt: Value(now),
      ));

      await _writeAuditLog('dispute_street', event.streetId,
          detail: event.disputeReason, entityType: 'street');
      emit(const QrActionSuccess('disputed'));
    } catch (e) {
      emit(QrError('Dispute failed: $e'));
    }
  }
}
