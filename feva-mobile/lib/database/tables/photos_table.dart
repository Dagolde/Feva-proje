import 'package:drift/drift.dart';

class Photos extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get photoId => text().unique()();
  TextColumn get recordType => text()(); // 'street' or 'building'
  IntColumn get recordLocalId => integer()(); // FK to streets.id or buildings.id
  TextColumn get filePath => text()(); // relative path within app storage
  IntColumn get isFrontage => integer().withDefault(const Constant(0))();
  RealColumn get latitude => real()();
  RealColumn get longitude => real()();
  IntColumn get capturedAt => integer()(); // Unix epoch ms (from EXIF)
  IntColumn get fileSizeBytes => integer().nullable()();
  IntColumn get brokenRefFlag => integer().withDefault(const Constant(0))();
  TextColumn get syncStatus =>
      text().withDefault(const Constant('queued'))();
  IntColumn get createdAt => integer().withDefault(const Constant(0))();
}
