import 'package:drift/drift.dart';

class SyncQueue extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get operation => text()(); // 'create','update','delete'
  TextColumn get entityType => text()(); // 'street','building','photo'
  IntColumn get entityLocalId => integer()();
  TextColumn get payloadJson => text()(); // serialised record snapshot
  IntColumn get attemptCount => integer().withDefault(const Constant(0))();
  IntColumn get lastAttemptAt => integer().nullable()();
  TextColumn get lastError => text().nullable()();
  TextColumn get status => text().withDefault(const Constant('pending'))();
  // 'pending','in_flight','done','failed'
  IntColumn get createdAt => integer().withDefault(const Constant(0))();
}
