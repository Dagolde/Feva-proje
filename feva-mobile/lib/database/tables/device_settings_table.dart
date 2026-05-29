import 'package:drift/drift.dart';

/// Stores device-level settings that should be reset when app data is cleared.
///
/// Storing device_id here (instead of flutter_secure_storage) ensures that
/// after an app data clear, a new device_id is generated. This allows the
/// backend to detect ID collisions from different "sessions" of the same
/// physical device and create distinct records.
class DeviceSettings extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get key => text().unique()();
  TextColumn get value => text()();
}
