import 'package:drift/drift.dart';

class DropdownConfig extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get category => text()(); // 'street_type','surface_type', etc.
  TextColumn get value => text()();
  TextColumn get label => text()();
  IntColumn get sortOrder => integer().withDefault(const Constant(0))();
  IntColumn get version => integer().withDefault(const Constant(1))();
  IntColumn get syncedAt => integer().withDefault(const Constant(0))();

  @override
  List<Set<Column>> get uniqueKeys => [
        {category, value},
      ];
}
