import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';

import 'package:drift/drift.dart' hide Column;
import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:path_provider/path_provider.dart';

import '../../boundary/boundary_service.dart';
import '../../database/app_database.dart';

part 'building_event.dart';
part 'building_state.dart';

/// Form data collected from [BuildingFormScreen].
class BuildingFormData extends Equatable {
  final String streetId; // FK to streets.street_id
  final String buildingType;
  final int numberOfFloors;
  final int numberOfUnits;
  final String buildingCondition;
  final String? notes;

  /// WKB-encoded Point geometry (EPSG:4326).
  final List<int> geometryWkb;

  /// GPS accuracy in metres.
  final double gpsAccuracyM;

  /// Local ID of the frontage photo in the [Photos] table.
  final int? frontagePhotoLocalId;

  /// Additional photo local IDs.
  final List<int> additionalPhotoLocalIds;

  final bool hasSignage;

  /// Business names — only relevant when [hasSignage] is true.
  final List<String> businessNames;

  final String lgaCode;
  final String enumeratorId;

  /// Street address auto-populated from the parent street record.
  final String? streetAddress;

  const BuildingFormData({
    required this.streetId,
    required this.buildingType,
    required this.numberOfFloors,
    required this.numberOfUnits,
    required this.buildingCondition,
    required this.geometryWkb,
    required this.gpsAccuracyM,
    required this.lgaCode,
    required this.enumeratorId,
    this.frontagePhotoLocalId,
    this.additionalPhotoLocalIds = const [],
    this.hasSignage = false,
    this.businessNames = const [],
    this.notes,
    this.streetAddress,
  });

  @override
  List<Object?> get props => [
        streetId,
        buildingType,
        numberOfFloors,
        numberOfUnits,
        buildingCondition,
        geometryWkb,
        gpsAccuracyM,
        frontagePhotoLocalId,
        additionalPhotoLocalIds,
        hasSignage,
        businessNames,
        lgaCode,
        enumeratorId,
        notes,
        streetAddress,
      ];
}

/// Manages building capture, listing, and persistence.
///
/// Requirements: 3.1–3.9
class BuildingBloc extends Bloc<BuildingEvent, BuildingState> {
  final AppDatabase db;
  final BoundaryService boundaryService;

  BuildingBloc({required this.db, required this.boundaryService})
      : super(const BuildingInitial()) {
    on<LoadBuildings>(_onLoadBuildings);
    on<SaveBuilding>(_onSaveBuilding);
    on<DeleteBuilding>(_onDeleteBuilding);
  }

  // ─── Event handlers ────────────────────────────────────────────────────────

  Future<void> _onLoadBuildings(
      LoadBuildings event, Emitter<BuildingState> emit) async {
    emit(const BuildingLoading());
    try {
      final buildings = await db.select(db.buildings).get();
      emit(BuildingListLoaded(buildings));
    } catch (e) {
      emit(BuildingError('Failed to load buildings: $e'));
    }
  }

  Future<void> _onSaveBuilding(
      SaveBuilding event, Emitter<BuildingState> emit) async {
    final data = event.formData;

    // ── Mandatory field validation (Requirements 3.2, 3.5, 3.6) ──────────
    final missing = await _validateMandatoryFields(data);
    if (missing.isNotEmpty) {
      emit(BuildingValidationError(missing));
      return;
    }

    emit(const BuildingSaving());
    try {
      final now = DateTime.now().millisecondsSinceEpoch;

      // ── Auto-generate building ID: BLD-[LGA]-[SEQ] (Requirement 3.1) ────
      final buildingId = await _generateBuildingId(data.lgaCode);

      // ── Decode first point from WKB for reverse geocode ──────────────────
      double lon = 0, lat = 0;
      if (data.geometryWkb.length >= 21) {
        final bytes = data.geometryWkb;
        final byteData = ByteData.sublistView(Uint8List.fromList(bytes));
        final isLe = bytes[0] == 1;
        // WKB Point: byteOrder(1) + wkbType(4) + X(8) + Y(8)
        lon = isLe
            ? byteData.getFloat64(5, Endian.little)
            : byteData.getFloat64(5, Endian.big);
        lat = isLe
            ? byteData.getFloat64(13, Endian.little)
            : byteData.getFloat64(13, Endian.big);
      }

      // ── Reverse geocode (Requirements 3.4, 10.1, 10.2, 10.3) ────────────
      final geo = await boundaryService.reverseGeocode(lon, lat,
          assignedLgaCode: data.lgaCode);

      final gpsAccuracyFlag = data.gpsAccuracyM > 10.0 ? 1 : 0;
      final businessNamesJson = data.hasSignage && data.businessNames.isNotEmpty
          ? jsonEncode(data.businessNames)
          : null;

      // ── Insert building row ───────────────────────────────────────────────
      // Look up parent street to get street_address for auto-population
      final parentStreet = await (db.select(db.streets)
            ..where((t) => t.streetId.equals(data.streetId)))
          .getSingleOrNull();

      final companion = BuildingsCompanion.insert(
        buildingId: buildingId,
        streetId: data.streetId,
        buildingType: data.buildingType,
        numberOfFloors: data.numberOfFloors,
        numberOfUnits: data.numberOfUnits,
        buildingCondition: data.buildingCondition,
        streetAddress: Value(parentStreet?.streetAddress),
        hasSignage: Value(data.hasSignage ? 1 : 0),
        businessNames: Value(businessNamesJson),
        notes: Value(data.notes),
        geometryWkb: Uint8List.fromList(data.geometryWkb),
        gpsAccuracyM: data.gpsAccuracyM,
        zone: Value(geo.zone),
        lga: data.lgaCode,
        ward: Value(geo.ward),
        postcode: Value(geo.postcode),
        postcodeStatus: Value(geo.postcodeStatus),
        enumeratorId: data.enumeratorId,
        enumerationDate: now,
        verificationStatus: const Value('pending'),
        boundaryFlag: Value(geo.boundaryFlag ? 1 : 0),
        gpsAccuracyFlag: Value(gpsAccuracyFlag),
        syncStatus: const Value('queued'),
        lastModifiedAt: Value(now),
        createdAt: Value(now),
      );

      final localId = await db.into(db.buildings).insert(companion);

      // ── Duplicate detection within 1 m (Requirements 11.2, 11.3) ─────────
      final building = await (db.select(db.buildings)
            ..where((t) => t.id.equals(localId)))
          .getSingle();

      await _checkAndFlagDuplicates(building, lat, lon);

      // ── Insert sync_queue entry (Requirement 6.4) ─────────────────────────
      final savedBuilding = await (db.select(db.buildings)
            ..where((t) => t.id.equals(localId)))
          .getSingle();

      await db.into(db.syncQueue).insert(SyncQueueCompanion.insert(
            operation: 'create',
            entityType: 'building',
            entityLocalId: localId,
            payloadJson: jsonEncode(_buildingToJson(savedBuilding)),
            status: const Value('pending'),
            createdAt: Value(now),
          ));

      // ── Enqueue photos for sync ───────────────────────────────────────────
      final photoIds = [
        if (data.frontagePhotoLocalId != null) data.frontagePhotoLocalId!,
        ...data.additionalPhotoLocalIds,
      ];
      for (final photoLocalId in photoIds) {
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
                  'record_type': 'building',
                  'record_local_id': localId,
                  'is_frontage': photo.isFrontage == 1,
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

      emit(BuildingSaved(savedBuilding));
    } catch (e) {
      emit(BuildingError('Failed to save building: $e'));
    }
  }

  Future<void> _onDeleteBuilding(
      DeleteBuilding event, Emitter<BuildingState> emit) async {
    try {
      await (db.delete(db.buildings)
            ..where((t) => t.id.equals(event.localId)))
          .go();
      add(const LoadBuildings());
    } catch (e) {
      emit(BuildingError('Failed to delete building: $e'));
    }
  }

  // ─── Helpers ───────────────────────────────────────────────────────────────

  /// Validates mandatory fields. Returns human-readable names of missing ones.
  Future<List<String>> _validateMandatoryFields(BuildingFormData data) async {
    final missing = <String>[];

    if (data.streetId.trim().isEmpty) {
      missing.add('Street ID');
    } else {
      // Verify street_id exists in local DB (Requirement 3.6).
      final exists = await (db.select(db.streets)
            ..where((t) => t.streetId.equals(data.streetId)))
          .getSingleOrNull();
      if (exists == null) missing.add('Street ID (not found)');
    }

    if (data.buildingType.trim().isEmpty) missing.add('Building Type');
    if (data.numberOfFloors <= 0) missing.add('Number of Floors');
    if (data.numberOfUnits <= 0) missing.add('Number of Units');
    if (data.buildingCondition.trim().isEmpty) missing.add('Building Condition');
    if (data.geometryWkb.isEmpty) missing.add('GPS Location');
    if (data.frontagePhotoLocalId == null) missing.add('Frontage Photo');

    return missing;
  }

  /// Generates the next `BLD-[LGA]-[SEQ]` identifier.
  Future<String> _generateBuildingId(String lgaCode) async {
    final prefix = 'BLD-$lgaCode-';
    final rows = await (db.select(db.buildings)
          ..where((t) => t.buildingId.like('$prefix%'))
          ..orderBy([(t) => OrderingTerm.desc(t.buildingId)])
          ..limit(1))
        .get();

    int nextSeq = 1;
    if (rows.isNotEmpty) {
      final lastId = rows.first.buildingId;
      final seqStr = lastId.substring(prefix.length);
      nextSeq = (int.tryParse(seqStr) ?? 0) + 1;
    }

    final seq = nextSeq.toString().padLeft(6, '0');
    return '$prefix$seq';
  }

  /// Checks all existing buildings for proximity < 1 m and flags duplicates.
  ///
  /// Requirements: 11.2, 11.3
  Future<void> _checkAndFlagDuplicates(
      Building newBuilding, double lat, double lon) async {
    final allBuildings = await db.select(db.buildings).get();
    final now = DateTime.now().millisecondsSinceEpoch;

    for (final existing in allBuildings) {
      if (existing.id == newBuilding.id) continue;
      if (existing.geometryWkb.length < 21) continue;

      // Decode existing building's WKB point
      final bytes = existing.geometryWkb;
      final byteData = ByteData.sublistView(Uint8List.fromList(bytes));
      final isLe = bytes[0] == 1;
      final eLon = isLe
          ? byteData.getFloat64(5, Endian.little)
          : byteData.getFloat64(5, Endian.big);
      final eLat = isLe
          ? byteData.getFloat64(13, Endian.little)
          : byteData.getFloat64(13, Endian.big);

      final distM = _haversineDistanceM(lat, lon, eLat, eLon);
      if (distM < 1.0) {
        // Flag the new building
        final newFlags = _addQaFlag(newBuilding.qaFlags, 'DUPLICATE_PROXIMITY');
        await (db.update(db.buildings)
              ..where((t) => t.id.equals(newBuilding.id)))
            .write(BuildingsCompanion(
          duplicateFlag: const Value(1),
          qaFlags: Value(newFlags),
          lastModifiedAt: Value(now),
        ));

        // Flag the existing building
        final existingFlags =
            _addQaFlag(existing.qaFlags, 'DUPLICATE_PROXIMITY');
        await (db.update(db.buildings)
              ..where((t) => t.id.equals(existing.id)))
            .write(BuildingsCompanion(
          duplicateFlag: const Value(1),
          qaFlags: Value(existingFlags),
          lastModifiedAt: Value(now),
        ));
      }
    }
  }

  /// Adds [flag] to the JSON array stored in [qaFlagsJson], deduplicating.
  String _addQaFlag(String? qaFlagsJson, String flag) {
    final List<dynamic> existing =
        qaFlagsJson != null ? jsonDecode(qaFlagsJson) as List<dynamic> : [];
    if (!existing.contains(flag)) existing.add(flag);
    return jsonEncode(existing);
  }

  /// Haversine distance in metres between two WGS-84 points.
  double _haversineDistanceM(
      double lat1, double lon1, double lat2, double lon2) {
    const r = 6371000.0; // Earth radius in metres
    final dLat = _toRad(lat2 - lat1);
    final dLon = _toRad(lon2 - lon1);
    final a = _sin2(dLat / 2) +
        _cos(_toRad(lat1)) * _cos(_toRad(lat2)) * _sin2(dLon / 2);
    final c = 2 * _atan2(sqrt(a), sqrt(1 - a));
    return r * c;
  }

  double _toRad(double deg) => deg * 3.141592653589793 / 180.0;
  double _sin2(double x) => sin(x) * sin(x);
  double _cos(double x) => cos(x);
  double _atan2(double y, double x) => atan2(y, x);

  Map<String, dynamic> _buildingToJson(Building b) {
    // Decode WKB Point for lat/lon fields.
    double lat = 0, lon = 0;
    final bytes = b.geometryWkb;
    if (bytes.length >= 21) {
      // Point WKB: byteOrder(1) + wkbType(4) + X(8) + Y(8)
      final bd = ByteData.sublistView(Uint8List.fromList(bytes));
      final isLe = bytes[0] == 1;
      lon = isLe ? bd.getFloat64(5, Endian.little) : bd.getFloat64(5, Endian.big);
      lat = isLe ? bd.getFloat64(13, Endian.little) : bd.getFloat64(13, Endian.big);
    }
    return {
      'building_id': b.buildingId,
      'street_id': b.streetId,
      'street_address': b.streetAddress,
      'building_type': b.buildingType,
      'number_of_floors': b.numberOfFloors,
      'number_of_units': b.numberOfUnits,
      'building_condition': b.buildingCondition,
      'has_signage': b.hasSignage,
      'business_names': b.businessNames,
      'notes': b.notes,
      'latitude': lat,
      'longitude': lon,
      'lga': b.lga,
      'zone': b.zone,
      'ward': b.ward,
      'postcode': b.postcode,
      'postcode_status': b.postcodeStatus,
      'enumerator_id': b.enumeratorId,
      'enumeration_date': b.enumerationDate,
      'verification_status': b.verificationStatus,
      'boundary_flag': b.boundaryFlag,
      'gps_accuracy_flag': b.gpsAccuracyFlag,
      'sync_status': b.syncStatus,
      'created_at': b.createdAt,
    };
  }
}
