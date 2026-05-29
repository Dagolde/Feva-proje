import 'package:drift/drift.dart';

class BoundaryZones extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get zoneId => text().unique()();
  TextColumn get zoneName => text()();
  TextColumn get zoneType => text()(); // 'lga','ward','nipost','admin'
  TextColumn get lgaCode => text().nullable()();
  TextColumn get wardCode => text().nullable()();
  TextColumn get postcode => text().nullable()();
  BlobColumn get geometryWkb => blob()(); // WKB polygon, EPSG:4326
  TextColumn get shapefileVersion => text()();
  IntColumn get createdAt => integer().withDefault(const Constant(0))();
}
