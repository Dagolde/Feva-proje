import 'package:drift/drift.dart';

class Sessions extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get userId => text()();
  TextColumn get username => text()();
  TextColumn get role => text()(); // 'enumerator','supervisor','admin'
  TextColumn get lgaCode => text().nullable()(); // LGA assignment from backend
  TextColumn get ward => text().nullable()(); // Ward assignment from backend
  TextColumn get accessToken => text()();
  TextColumn get refreshToken => text()();
  IntColumn get tokenExpiresAt => integer()(); // Unix epoch ms
  IntColumn get createdAt => integer().withDefault(const Constant(0))();
  // SHA-256 hash of password for offline login fallback
  TextColumn get passwordHash => text().nullable()();
}
