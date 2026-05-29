import 'package:drift/drift.dart';

class AuditLog extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get userId => text()();
  TextColumn get operation => text()();
  // 'login','logout','create','update','delete','sync','flag'
  TextColumn get entityType => text().nullable()();
  TextColumn get entityId => text().nullable()();
  TextColumn get detailJson => text().nullable()(); // additional context as JSON
  IntColumn get occurredAt => integer().withDefault(const Constant(0))();
}
