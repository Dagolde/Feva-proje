/// Result model returned by [PhotoService.captureAndStore].
class PhotoCaptureResult {
  /// UUID-style identifier generated at capture time.
  final String photoId;

  /// Relative path within app documents directory (e.g. `photos/<photoId>.jpg`).
  final String filePath;

  /// SQLite row ID of the inserted [Photos] row — use this as the photo local ID.
  final int localId;

  final double latitude;
  final double longitude;

  /// UTC timestamp when the photo was captured.
  final DateTime capturedAt;

  final int fileSizeBytes;

  /// True when this photo is the building frontage photo.
  final bool isFrontage;

  const PhotoCaptureResult({
    required this.photoId,
    required this.filePath,
    required this.localId,
    required this.latitude,
    required this.longitude,
    required this.capturedAt,
    required this.fileSizeBytes,
    required this.isFrontage,
  });
}
