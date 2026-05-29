import 'package:drift/drift.dart';

class Streets extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get streetId => text().unique()(); // STR-[LGA]-[SEQ]
  TextColumn get streetName => text()();
  TextColumn get streetAddress => text().withDefault(const Constant(''))();
  TextColumn get streetType => text()();
  TextColumn get surfaceType => text()();
  TextColumn get streetCondition => text()();
  TextColumn get notes => text().nullable()();
  BlobColumn get geometryWkb => blob()(); // WKB LineString, EPSG:4326
  TextColumn get zone => text().nullable()();
  TextColumn get lga => text()();
  TextColumn get ward => text().nullable()();
  TextColumn get enumeratorId => text()();
  IntColumn get enumerationDate => integer()(); // Unix epoch ms
  TextColumn get verificationStatus =>
      text().withDefault(const Constant('pending'))();
  IntColumn get boundaryFlag => integer().withDefault(const Constant(0))();
  IntColumn get gpsAccuracyFlag => integer().withDefault(const Constant(0))();
  TextColumn get qaFlags => text().nullable()(); // JSON array
  TextColumn get serverId => text().nullable()();
  TextColumn get syncStatus =>
      text().withDefault(const Constant('queued'))();
  IntColumn get lastModifiedAt => integer().withDefault(const Constant(0))();
  IntColumn get createdAt => integer().withDefault(const Constant(0))();
}
