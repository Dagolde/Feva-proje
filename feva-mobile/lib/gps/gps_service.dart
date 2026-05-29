/// GPS service wrapping the [geolocator] package.
///
/// Exposes a [Stream<GpsEvent>] with accuracy monitoring and a
/// [Future<GpsPositionReading>] for single-fix acquisition.
///
/// Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6

import 'dart:async';

import 'package:geolocator/geolocator.dart';

import 'gps_state.dart';

/// Exception thrown when [GpsService.getCurrentPosition] times out.
class GpsTimeoutException implements Exception {
  final String message;
  const GpsTimeoutException([this.message = 'GPS fix not obtained within 30 seconds']);

  @override
  String toString() => 'GpsTimeoutException: $message';
}

/// Core GPS service.
///
/// Intended to be used as a singleton — instantiate once and inject via
/// a service locator or provider.
///
/// ```dart
/// final gpsService = GpsService();
/// final permitted = await gpsService.requestPermission();
/// if (permitted) {
///   gpsService.streamPosition().listen((event) { ... });
/// }
/// ```
class GpsService {
  static const Duration _timeout = Duration(seconds: 30);

  static final LocationSettings _locationSettings = LocationSettings(
    accuracy: LocationAccuracy.high,
    distanceFilter: 0, // emit every fix
  );

  // ─── Public API ────────────────────────────────────────────────────────────

  /// Rounds [value] to exactly 5 decimal places.
  ///
  /// Used internally and exposed for testing / downstream consumers.
  static double roundTo5dp(double value) =>
      double.parse(value.toStringAsFixed(5));

  /// Checks and, if necessary, requests location permissions.
  ///
  /// Returns `true` when the app has [LocationPermission.always] or
  /// [LocationPermission.whileInUse]; `false` otherwise.
  Future<bool> requestPermission() async {
    LocationPermission permission = await Geolocator.checkPermission();

    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    return permission == LocationPermission.always ||
        permission == LocationPermission.whileInUse;
  }

  /// Starts streaming GPS events.
  ///
  /// Emits:
  /// - [GpsPositionEvent] on every new position fix.
  /// - [LowAccuracyWarning] (in addition to [GpsPositionEvent]) when
  ///   accuracy > 10 m (Requirement 4.4).
  /// - [GpsTimeout] if no fix is received within 30 seconds (Requirement 4.6).
  /// - [GpsError] on unrecoverable location provider errors.
  ///
  /// The stream is a broadcast stream; multiple listeners are supported.
  Stream<GpsEvent> streamPosition() {
    // Use a StreamController so we can inject the timeout event cleanly.
    final controller = StreamController<GpsEvent>.broadcast();

    Timer? timeoutTimer;
    StreamSubscription<Position>? positionSub;
    bool hasFix = false;

    void startTimeout() {
      timeoutTimer = Timer(_timeout, () {
        if (!hasFix && !controller.isClosed) {
          controller.add(GpsTimeout());
        }
      });
    }

    void onPosition(Position position) {
      hasFix = true;
      timeoutTimer?.cancel();

      final reading = _toReading(position);

      controller.add(GpsPositionEvent(reading));

      // Requirement 4.4: also emit LowAccuracyWarning when accuracy > 10 m.
      if (reading.isLowAccuracy) {
        controller.add(LowAccuracyWarning(reading));
      }
    }

    void onError(Object error, StackTrace stack) {
      controller.add(GpsError(error.toString()));
    }

    // Check permission then start streaming.
    Future(() async {
      final serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        controller.add(GpsError('Location services are disabled.'));
        return;
      }
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        controller.add(GpsError('Location permission denied.'));
        return;
      }

      // Start the timeout before subscribing so it covers the initial fix delay.
      startTimeout();

      positionSub = Geolocator.getPositionStream(
        locationSettings: _locationSettings,
      ).listen(
        onPosition,
        onError: onError,
        cancelOnError: false,
      );
    });

    // Clean up when the consumer cancels.
    controller.onCancel = () {
      timeoutTimer?.cancel();
      positionSub?.cancel();
    };

    return controller.stream;
  }

  /// Obtains a single GPS fix with a 30-second timeout.
  ///
  /// Automatically checks location services and requests permission if needed.
  /// Returns a [GpsPositionReading] on success.
  /// Throws [GpsTimeoutException] if no fix is obtained within 30 seconds.
  /// Throws [PermissionDeniedException] if location permission is not granted.
  Future<GpsPositionReading> getCurrentPosition() async {
    // Check if location services are enabled on the device.
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Location services are disabled. Please enable GPS in device settings.');
    }

    // Check and request permission.
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permission denied.');
      }
    }
    if (permission == LocationPermission.deniedForever) {
      throw Exception('Location permission permanently denied. Please enable it in app settings.');
    }

    try {
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      ).timeout(_timeout);

      return _toReading(position);
    } on TimeoutException {
      throw const GpsTimeoutException();
    }
  }

  // ─── Private helpers ───────────────────────────────────────────────────────

  /// Maps a [geolocator] [Position] to a [GpsPositionReading].
  ///
  /// Satellite count is set to null because [Position] does not expose it
  /// directly; a platform-specific implementation using Android's
  /// GnssStatus callback or iOS's CLLocation.course is required.
  GpsPositionReading _toReading(Position position) {
    return GpsPositionReading(
      latitude: position.latitude,
      longitude: position.longitude,
      accuracyMetres: position.accuracy,
      capturedAt: position.timestamp,
      satelliteCount: null, // not available via geolocator public API
    );
  }
}
