/// GPS state models and sealed event classes for the FEVA GPS service.
///
/// [GpsPositionReading] is the immutable data model for a GPS fix.
/// [GpsEvent] is the sealed class hierarchy emitted by [GpsService.streamPosition].

// ignore_for_file: invalid_annotation_target

import 'package:equatable/equatable.dart';

/// Immutable GPS position reading with 5 decimal place precision enforced.
///
/// Coordinates are rounded to exactly 5 decimal places on construction to
/// satisfy Requirements 4.3, 2.3, 3.3.
class GpsPositionReading extends Equatable {
  /// Latitude rounded to 5 decimal places (e.g. 6.45123).
  final double latitude;

  /// Longitude rounded to 5 decimal places (e.g. 3.39876).
  final double longitude;

  /// Reported horizontal accuracy in metres from the location provider.
  final double accuracyMetres;

  /// Satellite count — null when not available from the platform.
  ///
  /// Note: geolocator's [Position] does not expose satellite count directly;
  /// a platform-specific implementation (e.g. native Android LocationManager
  /// GnssStatus callback) is required to populate this field.
  final int? satelliteCount;

  /// UTC timestamp when this fix was captured.
  final DateTime capturedAt;

  /// True when [accuracyMetres] > 10.0 — triggers Supervisor review flag.
  final bool isLowAccuracy;

  /// True when the user typed coordinates manually (GPS timeout fallback).
  /// Records with this flag carry [accuracyMetres] == 999.0 as a sentinel.
  final bool isManualEntry;

  const GpsPositionReading._({
    required this.latitude,
    required this.longitude,
    required this.accuracyMetres,
    required this.capturedAt,
    required this.isLowAccuracy,
    required this.isManualEntry,
    this.satelliteCount,
  });

  /// Factory constructor that enforces 5 decimal place precision on [lat]/[lon].
  factory GpsPositionReading({
    required double latitude,
    required double longitude,
    required double accuracyMetres,
    required DateTime capturedAt,
    int? satelliteCount,
    bool isManualEntry = false,
  }) {
    final roundedLat = _roundTo5dp(latitude);
    final roundedLon = _roundTo5dp(longitude);
    return GpsPositionReading._(
      latitude: roundedLat,
      longitude: roundedLon,
      accuracyMetres: accuracyMetres,
      capturedAt: capturedAt,
      satelliteCount: satelliteCount,
      isLowAccuracy: accuracyMetres > 10.0,
      isManualEntry: isManualEntry,
    );
  }

  /// Rounds [value] to exactly 5 decimal places.
  static double _roundTo5dp(double value) =>
      double.parse(value.toStringAsFixed(5));

  @override
  List<Object?> get props => [
        latitude,
        longitude,
        accuracyMetres,
        satelliteCount,
        capturedAt,
        isLowAccuracy,
        isManualEntry,
      ];

  @override
  String toString() =>
      'GpsPositionReading(lat=$latitude, lon=$longitude, '
      'accuracy=${accuracyMetres}m, satellites=$satelliteCount, '
      'lowAccuracy=$isLowAccuracy, manual=$isManualEntry)';
}

// ─── GPS Event sealed class hierarchy ────────────────────────────────────────

/// Sealed base class for all events emitted by [GpsService.streamPosition].
sealed class GpsEvent {}

/// Emitted on every new position fix from the location provider.
final class GpsPositionEvent extends GpsEvent {
  final GpsPositionReading reading;
  GpsPositionEvent(this.reading);
}

/// Emitted in addition to [GpsPositionEvent] when [GpsPositionReading.isLowAccuracy]
/// is true (accuracy > 10 m). Requirement 4.4: flag record for Supervisor review.
final class LowAccuracyWarning extends GpsEvent {
  final GpsPositionReading reading;
  LowAccuracyWarning(this.reading);
}

/// Emitted when no GPS fix is obtained within the 30-second timeout window.
/// Requirement 4.6: notify Enumerator and offer retry / manual entry.
final class GpsTimeout extends GpsEvent {
  GpsTimeout();
}

/// Emitted when the location provider returns an unrecoverable error.
final class GpsError extends GpsEvent {
  final String message;
  GpsError(this.message);
}
