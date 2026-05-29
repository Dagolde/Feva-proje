import 'dart:convert';
import 'dart:typed_data';

import 'package:drift/drift.dart' hide Column;
import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:path_provider/path_provider.dart';

import '../../boundary/boundary_service.dart';
import '../../database/app_database.dart';

part 'street_event.dart';
part 'street_state.dart';

/// Form data collected from [StreetFormScreen].
class StreetFormData extends Equatable {
  final String streetName;
  final String streetAddress;
  final String streetType;
  final String surfaceType;
  final String streetCondition;
  final String? notes;

  /// WKB-encoded LineString geometry (EPSG:4326).
  final List<int> geometryWkb;

  /// GPS accuracy in metres for the captured geometry.
  final double gpsAccuracyM;

  /// Local IDs of photos already inserted into the [Photos] table.
  final List<int> photoLocalIds;

  /// LGA code from the enumerator's session — used for ID generation and
  /// boundary checking.
  final String lgaCode;

  /// Enumerator user ID from the active session.
  final String enumeratorId;

  const StreetFormData({
    required this.streetName,
    required this.streetAddress,
    required this.streetType,
    required this.surfaceType,
    required this.streetCondition,
    required this.geometryWkb,
    required this.gpsAccuracyM,
    required this.photoLocalIds,
    required this.lgaCode,
    required this.enumeratorId,
    this.notes,
  });

  @override
  List<Object?> get props => [
        streetName,
        streetAddress,
        streetType,
        surfaceType,
        streetCondition,
        geometryWkb,
        gpsAccuracyM,
        photoLocalIds,
        lgaCode,
        enumeratorId,
        notes,
      ];
}

/// Manages street capture, listing, and persistence.
///
/// Requirements: 2.1–2.8
class StreetBloc extends Bloc<StreetEvent, StreetState> {
  final AppDatabase db;
  final BoundaryService boundaryService;

  StreetBloc({required this.db, required this.boundaryService})
      : super(const StreetInitial()) {
    on<LoadStreets>(_onLoadStreets);
    on<SaveStreet>(_onSaveStreet);
    on<DeleteStreet>(_onDeleteStreet);
  }

  // ─── Event handlers ────────────────────────────────────────────────────────

  Future<void> _onLoadStreets(
      LoadStreets event, Emitter<StreetState> emit) async {
    emit(const StreetLoading());
    try {
      final streets = await db.select(db.streets).get();
      emit(StreetListLoaded(streets));
    } catch (e) {
      emit(StreetError('Failed to load streets: $e'));
    }
  }

  Future<void> _onSaveStreet(
      SaveStreet event, Emitter<StreetState> emit) async {
    final data = event.formData;

    // ── Mandatory field validation (Requirement 2.5) ──────────────────────
    final missing = _validateMandatoryFields(data);
    if (missing.isNotEmpty) {
      emit(StreetValidationError(missing));
      return;
    }

    emit(const StreetSaving());
    try {
      final now = DateTime.now().millisecondsSinceEpoch;

      // ── Auto-generate street ID: STR-[LGA]-[SEQ] (Requirement 2.1) ──────
      final streetId = await _generateStreetId(data.lgaCode);

      // ── Reverse geocode to populate zone/lga/ward (Requirement 2.4) ─────
      // Decode the first point from the WKB LineString for geocoding.
      // For simplicity we use the GPS reading's first coordinate pair.
      // A full WKB decode is handled by WkbPolygon; here we pass the
      // centroid approximation via the first 2 doubles in the payload.
      double lon = 0, lat = 0;
      if (data.geometryWkb.length >= 21) {
        // WKB Point layout: 1 byte order + 4 type + 8 lon + 8 lat = 21 bytes
        // LineString: 1 + 4 + 4 (numPoints) + 16*n — first point at offset 9
        final bytes = data.geometryWkb;
        final byteData = ByteData.sublistView(Uint8List.fromList(bytes));
        final isLe = bytes[0] == 1;
        // Skip: byteOrder(1) + wkbType(4) + numPoints(4) = 9 bytes
        lon = isLe
            ? byteData.getFloat64(9, Endian.little)
            : byteData.getFloat64(9, Endian.big);
        lat = isLe
            ? byteData.getFloat64(17, Endian.little)
            : byteData.getFloat64(17, Endian.big);
      }

      final geo = await boundaryService.reverseGeocode(lon, lat,
          assignedLgaCode: data.lgaCode);

      final gpsAccuracyFlag = data.gpsAccuracyM > 10.0 ? 1 : 0;

      // ── Insert street row ─────────────────────────────────────────────────
      final companion = StreetsCompanion.insert(
        streetId: streetId,
        streetName: data.streetName,
        streetAddress: Value(data.streetAddress),
        streetType: data.streetType,
        surfaceType: data.surfaceType,
        streetCondition: data.streetCondition,
        notes: Value(data.notes),
        geometryWkb: Uint8List.fromList(data.geometryWkb),
        zone: Value(geo.zone),
        lga: data.lgaCode,
        ward: Value(geo.ward),
        enumeratorId: data.enumeratorId,
        enumerationDate: now,
        verificationStatus: const Value('pending'),
        boundaryFlag: Value(geo.boundaryFlag ? 1 : 0),
        gpsAccuracyFlag: Value(gpsAccuracyFlag),
        syncStatus: const Value('queued'),
        lastModifiedAt: Value(now),
        createdAt: Value(now),
      );

      final localId = await db.into(db.streets).insert(companion);

      // ── Insert sync_queue entry (Requirement 6.4) ─────────────────────────
      final street = await (db.select(db.streets)
            ..where((t) => t.id.equals(localId)))
          .getSingle();

      await db.into(db.syncQueue).insert(SyncQueueCompanion.insert(
            operation: 'create',
            entityType: 'street',
            entityLocalId: localId,
            payloadJson: jsonEncode(_streetToJson(street)),
            status: const Value('pending'),
            createdAt: Value(now),
          ));

      // ── Enqueue photos for sync ───────────────────────────────────────────
      for (final photoLocalId in data.photoLocalIds) {
        final photo = await (db.select(db.photos)
              ..where((t) => t.id.equals(photoLocalId)))
            .getSingleOrNull();
        if (photo != null) {
          final appDocDir = await getApplicationDocumentsDirectory();
          final absolutePath = '${appDocDir.path}/${photo.filePath}';
          await db.into(db.syncQueue).insert(SyncQueueCompanion.insert(
                operation: 'create',
                entityType: 'photo',
                entityLocalId: photoLocalId,
                payloadJson: jsonEncode({
                  'photo_id': photo.photoId,
                  'record_type': 'street',
                  'record_local_id': localId,
                  'is_frontage': false,
                  'captured_at': photo.capturedAt,
                  'latitude': photo.latitude,
                  'longitude': photo.longitude,
                  'filename': '${photo.photoId}.jpg',
                  'file_path': absolutePath,
                }),
                status: const Value('pending'),
                createdAt: Value(now),
              ));
        }
      }

      emit(StreetSaved(street));
    } catch (e) {
      emit(StreetError('Failed to save street: $e'));
    }
  }

  Future<void> _onDeleteStreet(
      DeleteStreet event, Emitter<StreetState> emit) async {
    try {
      await (db.delete(db.streets)
            ..where((t) => t.id.equals(event.localId)))
          .go();
      add(const LoadStreets());
    } catch (e) {
      emit(StreetError('Failed to delete street: $e'));
    }
  }

  // ─── Helpers ───────────────────────────────────────────────────────────────

  /// Validates mandatory fields. Returns a list of human-readable field names
  /// that are missing or invalid.
  List<String> _validateMandatoryFields(StreetFormData data) {
    final missing = <String>[];
    if (data.streetName.trim().isEmpty) missing.add('Street Name');
    if (data.streetAddress.trim().isEmpty) missing.add('Street Address');
    if (data.streetType.trim().isEmpty) missing.add('Street Type');
    if (data.surfaceType.trim().isEmpty) missing.add('Surface Type');
    if (data.streetCondition.trim().isEmpty) missing.add('Street Condition');
    if (data.geometryWkb.isEmpty) missing.add('GPS Location');
    if (data.photoLocalIds.isEmpty) missing.add('At least one geotagged photo');
    return missing;
  }

  /// Generates the next `STR-[LGA]-[SEQ]` identifier.
  ///
  /// Queries `MAX(street_id)` for the given [lgaCode] to derive the next
  /// 6-digit zero-padded sequence number (Requirement 2.1).
  Future<String> _generateStreetId(String lgaCode) async {
    final prefix = 'STR-$lgaCode-';
    final rows = await (db.select(db.streets)
          ..where((t) => t.streetId.like('$prefix%'))
          ..orderBy([(t) => OrderingTerm.desc(t.streetId)])
          ..limit(1))
        .get();

    int nextSeq = 1;
    if (rows.isNotEmpty) {
      final lastId = rows.first.streetId; // e.g. STR-LAGOS-000042
      final seqStr = lastId.substring(prefix.length);
      nextSeq = (int.tryParse(seqStr) ?? 0) + 1;
    }

    final seq = nextSeq.toString().padLeft(6, '0');
    return '$prefix$seq';
  }

  Map<String, dynamic> _streetToJson(Street s) {
    // Decode all points from WKB LineString.
    // WKB layout: byteOrder(1) + wkbType(4) + numPoints(4) + [X(8)+Y(8)]*N
    double lat = 0, lon = 0;
    final coordinates = <List<double>>[];
    final bytes = s.geometryWkb;
    if (bytes.length >= 25) {
      final bd = ByteData.sublistView(Uint8List.fromList(bytes));
      final isLe = bytes[0] == 1;
      final numPoints = isLe
          ? bd.getUint32(5, Endian.little)
          : bd.getUint32(5, Endian.big);
      int offset = 9;
      for (int i = 0; i < numPoints && offset + 16 <= bytes.length; i++) {
        final x = isLe
            ? bd.getFloat64(offset, Endian.little)
            : bd.getFloat64(offset, Endian.big);
        final y = isLe
            ? bd.getFloat64(offset + 8, Endian.little)
            : bd.getFloat64(offset + 8, Endian.big);
        coordinates.add([x, y]); // [lon, lat]
        offset += 16;
      }
      if (coordinates.isNotEmpty) {
        lon = coordinates[0][0];
        lat = coordinates[0][1];
      }
    }
    return {
      'street_id': s.streetId,
      'street_name': s.streetName,
      'street_address': s.streetAddress,
      'street_type': s.streetType,
      'surface_type': s.surfaceType,
      'street_condition': s.streetCondition,
      'notes': s.notes,
      'latitude': lat,
      'longitude': lon,
      'coordinates': coordinates, // full GPS track for QA map
      'lga': s.lga,
      'zone': s.zone,
      'ward': s.ward,
      'enumerator_id': s.enumeratorId,
      'enumeration_date': s.enumerationDate,
      'verification_status': s.verificationStatus,
      'boundary_flag': s.boundaryFlag,
      'gps_accuracy_flag': s.gpsAccuracyFlag,
      'sync_status': s.syncStatus,
      'created_at': s.createdAt,
    };
  }
}
