import 'dart:io';

import 'package:camera/camera.dart';
import 'package:drift/drift.dart';
import 'package:native_exif/native_exif.dart';
import 'package:path_provider/path_provider.dart';

import '../database/app_database.dart';
import '../gps/gps_state.dart';
import 'models/photo_capture_result.dart';

/// Wraps the `camera` package to capture photos, inject EXIF metadata, persist
/// the file to app-private storage, and record the result in the [Photos] table.
///
/// Supports multiple photos per street or building record (Requirements 5.1, 5.2, 5.5).
class PhotoService {
  final AppDatabase db;

  /// User ID written to audit log entries.
  final String userId;

  PhotoService({required this.db, required this.userId});

  /// Stores a photo from an already-captured [XFile], injects GPS + timestamp
  /// EXIF data, persists the file to app-private storage, and inserts a row
  /// into the [Photos] table.
  ///
  /// Use this when the [XFile] was obtained from a [CameraScreen] or
  /// image picker rather than directly from a [CameraController].
  Future<PhotoCaptureResult> storeXFile({
    required XFile xFile,
    required GpsPositionReading gpsReading,
    required String recordType,
    required int recordLocalId,
    bool isFrontage = false,
  }) async {
    // 1. Resolve the app documents directory.
    final appDocDir = await getApplicationDocumentsDirectory();
    final photosDir = Directory('${appDocDir.path}/photos');
    if (!photosDir.existsSync()) {
      photosDir.createSync(recursive: true);
    }

    // 2. Generate a unique photo ID.
    final photoId =
        '${DateTime.now().millisecondsSinceEpoch}_${recordType}_$recordLocalId';

    // 3. Copy the captured file to the permanent location.
    final absolutePath = '${photosDir.path}/$photoId.jpg';
    await File(xFile.path).copy(absolutePath);

    // 4. Relative path stored in the DB.
    final relativePath = 'photos/$photoId.jpg';

    // 5. Inject EXIF metadata (GPS + timestamp).
    final exif = await Exif.fromPath(absolutePath);
    await exif.writeAttributes({
      'GPSLatitude': gpsReading.latitude.toString(),
      'GPSLongitude': gpsReading.longitude.toString(),
      'DateTimeOriginal': _formatExifDateTime(gpsReading.capturedAt),
    });
    await exif.close();

    // 6. Measure file size after EXIF write.
    final fileSizeBytes = File(absolutePath).lengthSync();

    // 7. Persist to the photos table and get the inserted row ID.
    final insertedId = await db.into(db.photos).insert(PhotosCompanion.insert(
          photoId: photoId,
          recordType: recordType,
          recordLocalId: recordLocalId,
          filePath: relativePath,
          isFrontage: Value(isFrontage ? 1 : 0),
          latitude: gpsReading.latitude,
          longitude: gpsReading.longitude,
          capturedAt: gpsReading.capturedAt.millisecondsSinceEpoch,
          fileSizeBytes: Value(fileSizeBytes),
          createdAt: Value(DateTime.now().millisecondsSinceEpoch),
        ));

    return PhotoCaptureResult(
      photoId: photoId,
      filePath: relativePath,
      localId: insertedId,
      latitude: gpsReading.latitude,
      longitude: gpsReading.longitude,
      capturedAt: gpsReading.capturedAt,
      fileSizeBytes: fileSizeBytes,
      isFrontage: isFrontage,
    );
  }

  /// Captures a photo using [controller], injects GPS + timestamp EXIF data,
  /// stores the file under `{appDocDir}/photos/`, and inserts a row into the
  /// [Photos] table.
  ///
  /// - [gpsReading] — the current GPS fix to embed in EXIF.
  /// - [recordType] — `'street'` or `'building'`.
  /// - [recordLocalId] — the SQLite `id` of the parent street/building record.
  /// - [isFrontage] — `true` when this is the building frontage photo.
  ///
  /// Returns a [PhotoCaptureResult] on success.
  Future<PhotoCaptureResult> captureAndStore({
    required CameraController controller,
    required GpsPositionReading gpsReading,
    required String recordType,
    required int recordLocalId,
    bool isFrontage = false,
  }) async {
    // 1. Take the picture.
    final xFile = await controller.takePicture();

    // 2. Resolve the app documents directory.
    final appDocDir = await getApplicationDocumentsDirectory();
    final photosDir = Directory('${appDocDir.path}/photos');
    if (!photosDir.existsSync()) {
      photosDir.createSync(recursive: true);
    }

    // 3. Generate a unique photo ID (no uuid package — use timestamp + context).
    final photoId =
        '${DateTime.now().millisecondsSinceEpoch}_${recordType}_$recordLocalId';

    // 4. Copy the captured file to the permanent location.
    final absolutePath = '${photosDir.path}/$photoId.jpg';
    await File(xFile.path).copy(absolutePath);

    // 5. Relative path stored in the DB.
    final relativePath = 'photos/$photoId.jpg';

    // 6. Inject EXIF metadata (GPS + timestamp).
    final exif = await Exif.fromPath(absolutePath);
    await exif.writeAttributes({
      'GPSLatitude': gpsReading.latitude.toString(),
      'GPSLongitude': gpsReading.longitude.toString(),
      'DateTimeOriginal': _formatExifDateTime(gpsReading.capturedAt),
    });
    await exif.close();

    // 7. Measure file size after EXIF write.
    final fileSizeBytes = File(absolutePath).lengthSync();

    // 8. Persist to the photos table and get the inserted row ID.
    final insertedId = await db.into(db.photos).insert(PhotosCompanion.insert(
          photoId: photoId,
          recordType: recordType,
          recordLocalId: recordLocalId,
          filePath: relativePath,
          isFrontage: Value(isFrontage ? 1 : 0),
          latitude: gpsReading.latitude,
          longitude: gpsReading.longitude,
          capturedAt: gpsReading.capturedAt.millisecondsSinceEpoch,
          fileSizeBytes: Value(fileSizeBytes),
          createdAt: Value(DateTime.now().millisecondsSinceEpoch),
        ));

    return PhotoCaptureResult(
      photoId: photoId,
      filePath: relativePath,
      localId: insertedId,
      latitude: gpsReading.latitude,
      longitude: gpsReading.longitude,
      capturedAt: gpsReading.capturedAt,
      fileSizeBytes: fileSizeBytes,
      isFrontage: isFrontage,
    );
  }

  /// Formats [dt] as `'yyyy:MM:dd HH:mm:ss'` for the EXIF `DateTimeOriginal` tag.
  String _formatExifDateTime(DateTime dt) {
    final y = dt.year.toString().padLeft(4, '0');
    final mo = dt.month.toString().padLeft(2, '0');
    final d = dt.day.toString().padLeft(2, '0');
    final h = dt.hour.toString().padLeft(2, '0');
    final mi = dt.minute.toString().padLeft(2, '0');
    final s = dt.second.toString().padLeft(2, '0');
    return '$y:$mo:$d $h:$mi:$s';
  }
}
