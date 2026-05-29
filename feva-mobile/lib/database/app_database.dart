import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;

import 'tables/audit_log_table.dart';
import 'tables/boundary_zones_table.dart';
import 'tables/buildings_table.dart';
import 'tables/device_settings_table.dart';
import 'tables/dropdown_config_table.dart';
import 'tables/photos_table.dart';
import 'tables/sessions_table.dart';
import 'tables/streets_table.dart';
import 'tables/sync_queue_table.dart';

part 'app_database.g.dart';

const _kDbName = 'feva.db';

Future<QueryExecutor> _openDatabase() async {
  // Hardcoded path for Android - avoids path_provider plugin issues
  // Android apps always have access to their data directory
  final dbFolder = Directory('/data/data/com.igsl.feva/databases');
  if (!dbFolder.existsSync()) {
    dbFolder.createSync(recursive: true);
  }
  
  final file = File(p.join(dbFolder.path, _kDbName));

  // Using unencrypted database for now
  // TODO: Add encryption back once path_provider issues are resolved
  return NativeDatabase.createInBackground(file);
}

@DriftDatabase(tables: [
  Sessions,
  DropdownConfig,
  BoundaryZones,
  Streets,
  Buildings,
  Photos,
  SyncQueue,
  AuditLog,
  DeviceSettings,
])
class AppDatabase extends _$AppDatabase {
  AppDatabase(super.e);

  static Future<AppDatabase> open() async {
    final executor = await _openDatabase();
    return AppDatabase(executor);
  }

  @override
  int get schemaVersion => 6;

  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (m) async {
          await m.createAll();
          await _seedDropdownConfig();
        },
        onUpgrade: (m, from, to) async {
          if (from < 2) {
            await m.addColumn(sessions, sessions.lgaCode);
          }
          if (from < 3) {
            await m.addColumn(sessions, sessions.passwordHash);
          }
          if (from < 4) {
            await m.addColumn(sessions, sessions.ward);
          }
          if (from < 5) {
            await m.createTable(deviceSettings);
          }
          if (from < 6) {
            await m.database.customStatement(
                "ALTER TABLE streets ADD COLUMN street_address TEXT NOT NULL DEFAULT ''");
            await m.database.customStatement(
                'ALTER TABLE buildings ADD COLUMN street_address TEXT');
          }
        },
      );

  /// Seeds default dropdown configuration values on first database creation.
  /// This provides offline fallback values before the first sync from server.
  Future<void> _seedDropdownConfig() async {
    final now = DateTime.now().millisecondsSinceEpoch;
    
    // Street Types
    await batch((batch) {
      batch.insertAll(dropdownConfig, [
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'avenue', label: 'Avenue',
          sortOrder: const Value(1), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'boulevard', label: 'Boulevard',
          sortOrder: const Value(2), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'close', label: 'Close',
          sortOrder: const Value(3), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'crescent', label: 'Crescent',
          sortOrder: const Value(4), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'drive', label: 'Drive',
          sortOrder: const Value(5), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'lane', label: 'Lane',
          sortOrder: const Value(6), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'road', label: 'Road',
          sortOrder: const Value(7), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'street', label: 'Street',
          sortOrder: const Value(8), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_type', value: 'way', label: 'Way',
          sortOrder: const Value(9), version: const Value(1), syncedAt: Value(now),
        ),
        // Surface Types
        DropdownConfigCompanion.insert(
          category: 'surface_type', value: 'asphalt', label: 'Asphalt',
          sortOrder: const Value(1), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'surface_type', value: 'concrete', label: 'Concrete',
          sortOrder: const Value(2), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'surface_type', value: 'gravel', label: 'Gravel',
          sortOrder: const Value(3), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'surface_type', value: 'dirt', label: 'Dirt',
          sortOrder: const Value(4), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'surface_type', value: 'paved_blocks', label: 'Paved Blocks',
          sortOrder: const Value(5), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'surface_type', value: 'unpaved', label: 'Unpaved',
          sortOrder: const Value(6), version: const Value(1), syncedAt: Value(now),
        ),
        // Street Conditions
        DropdownConfigCompanion.insert(
          category: 'street_condition', value: 'excellent', label: 'Excellent',
          sortOrder: const Value(1), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_condition', value: 'good', label: 'Good',
          sortOrder: const Value(2), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_condition', value: 'fair', label: 'Fair',
          sortOrder: const Value(3), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_condition', value: 'poor', label: 'Poor',
          sortOrder: const Value(4), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'street_condition', value: 'very_poor', label: 'Very Poor',
          sortOrder: const Value(5), version: const Value(1), syncedAt: Value(now),
        ),
        // Building Types
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'residential', label: 'Residential',
          sortOrder: const Value(1), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'commercial', label: 'Commercial',
          sortOrder: const Value(2), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'industrial', label: 'Industrial',
          sortOrder: const Value(3), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'mixed_use', label: 'Mixed Use',
          sortOrder: const Value(4), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'institutional', label: 'Institutional',
          sortOrder: const Value(5), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'religious', label: 'Religious',
          sortOrder: const Value(6), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'educational', label: 'Educational',
          sortOrder: const Value(7), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'healthcare', label: 'Healthcare',
          sortOrder: const Value(8), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'government', label: 'Government',
          sortOrder: const Value(9), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_type', value: 'recreational', label: 'Recreational',
          sortOrder: const Value(10), version: const Value(1), syncedAt: Value(now),
        ),
        // Building Conditions
        DropdownConfigCompanion.insert(
          category: 'building_condition', value: 'excellent', label: 'Excellent',
          sortOrder: const Value(1), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_condition', value: 'good', label: 'Good',
          sortOrder: const Value(2), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_condition', value: 'fair', label: 'Fair',
          sortOrder: const Value(3), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_condition', value: 'poor', label: 'Poor',
          sortOrder: const Value(4), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_condition', value: 'very_poor', label: 'Very Poor',
          sortOrder: const Value(5), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_condition', value: 'under_construction', label: 'Under Construction',
          sortOrder: const Value(6), version: const Value(1), syncedAt: Value(now),
        ),
        DropdownConfigCompanion.insert(
          category: 'building_condition', value: 'abandoned', label: 'Abandoned',
          sortOrder: const Value(7), version: const Value(1), syncedAt: Value(now),
        ),
      ]);
    });
  }

  @override
  Future<void> close() => executor.close();
}
