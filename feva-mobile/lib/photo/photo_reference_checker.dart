import 'dart:io';

import 'package:drift/drift.dart';

import '../database/app_database.dart';

/// Scans queued photo records for missing files and flags broken references.
///
/// Before any sync attempt, call [checkAndFlagBrokenReferences] to detect
/// photos whose files have been deleted or moved since capture (Requirement 5.3).
class PhotoReferenceChecker {
  final AppDatabase db;

  /// User ID written to audit log entries.
  final String userId;

  PhotoReferenceChecker({required this.db, required this.userId});

  /// Scans all [Photos] rows with `sync_status = 'queued'`, checks whether
  /// each file exists on disk, and for any missing file:
  ///   - sets `broken_ref_flag = 1`
  ///   - writes an entry to [AuditLog]
  ///
  /// [appDocDirPath] — the absolute path returned by
  /// `getApplicationDocumentsDirectory()`.
  ///
  /// Returns the count of broken references found.
  Future<int> checkAndFlagBrokenReferences(String appDocDirPath) async {
    // 1. Fetch all queued photos.
    final queued = await (db.select(db.photos)
          ..where((p) => p.syncStatus.equals('queued')))
        .get();

    int brokenCount = 0;

    for (final row in queued) {
      final absolutePath = '$appDocDirPath/${row.filePath}';
      final exists = File(absolutePath).existsSync();

      if (!exists) {
        brokenCount++;

        // 2. Set broken_ref_flag = 1.
        await (db.update(db.photos)..where((p) => p.id.equals(row.id)))
            .write(PhotosCompanion(brokenRefFlag: const Value(1)));

        // 3. Write audit log entry.
        await db.into(db.auditLog).insert(AuditLogCompanion.insert(
              userId: userId,
              operation: 'flag',
              entityType: const Value('photo'),
              entityId: Value(row.photoId),
              detailJson: Value(
                '{"reason":"broken_ref","path":"${row.filePath}"}',
              ),
              occurredAt:
                  Value(DateTime.now().millisecondsSinceEpoch),
            ));
      }
    }

    return brokenCount;
  }

  /// Returns all [Photo] rows that have `broken_ref_flag = 1`.
  Future<List<Photo>> getBrokenRefPhotos() async {
    return (db.select(db.photos)
          ..where((p) => p.brokenRefFlag.equals(1)))
        .get();
  }
}
