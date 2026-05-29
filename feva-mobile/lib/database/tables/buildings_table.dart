import 'package:drift/drift.dart';

class Buildings extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get buildingId => text().unique()(); // BLD-[LGA]-[SEQ]
  TextColumn get streetId => text()(); // FK to streets.street_id
  TextColumn get buildingType => text()();
  IntColumn get numberOfFloors => integer()();
  IntColumn get numberOfUnits => integer()();
  TextColumn get buildingCondition => text()();
  TextColumn get streetAddress => text().nullable()();
  IntColumn get hasSignage => integer().withDefault(const Constant(0))(); // boolean
  TextColumn get businessNames => text().nullable()(); // JSON array
  TextColumn get notes => text().nullable()();
  BlobColumn get geometryWkb => blob()(); // WKB Point, EPSG:4326
  RealColumn get gpsAccuracyM => real()();
  TextColumn get zone => text().nullable()();
  TextColumn get lga => text()();
  TextColumn get ward => text().nullable()();
  TextColumn get postcode => text().nullable()();
  TextColumn get postcodeStatus =>
      text().withDefault(const Constant('resolved'))();
  TextColumn get enumeratorId => text()();
  IntColumn get enumerationDate => integer()();
  TextColumn get verificationStatus =>
      text().withDefault(const Constant('pending'))();
  TextColumn get rejectionReason => text().nullable()();
  TextColumn get disputeReason => text().nullable()();
  TextColumn get verifiedBy => text().nullable()();
  IntColumn get verifiedAt => integer().nullable()();
  IntColumn get boundaryFlag => integer().withDefault(const Constant(0))();
  IntColumn get gpsAccuracyFlag => integer().withDefault(const Constant(0))();
  IntColumn get duplicateFlag => integer().withDefault(const Constant(0))();
  TextColumn get qaFlags => text().nullable()(); // JSON array
  TextColumn get serverId => text().nullable()();
  TextColumn get syncStatus =>
      text().withDefault(const Constant('queued'))();
  IntColumn get lastModifiedAt => integer().withDefault(const Constant(0))();
  IntColumn get createdAt => integer().withDefault(const Constant(0))();
}
