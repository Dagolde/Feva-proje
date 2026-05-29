/// Real-time GPS accuracy and satellite count display widget.
///
/// Displays the current accuracy estimate and satellite count to the
/// Enumerator during GPS acquisition (Requirement 4.5).

import 'package:flutter/material.dart';

import '../gps_state.dart';

/// Displays GPS accuracy and satellite count from a [GpsPositionReading].
///
/// - Accuracy text is green when ≤ 10 m, red when > 10 m.
/// - Shows a green GPS icon when accuracy is good, orange warning icon otherwise.
/// - Satellite count shows "N/A" when [GpsPositionReading.satelliteCount] is null.
///
/// Pass `null` for [reading] to show a "Acquiring GPS…" placeholder.
class GpsAccuracyWidget extends StatelessWidget {
  /// The latest GPS reading, or null while acquiring.
  final GpsPositionReading? reading;

  const GpsAccuracyWidget({super.key, this.reading});

  @override
  Widget build(BuildContext context) {
    if (reading == null) {
      return _buildAcquiring(context);
    }

    final isGood = !reading!.isLowAccuracy;
    final accuracyColor = isGood ? Colors.green : Colors.red;
    final statusIcon = isGood
        ? const Icon(Icons.gps_fixed, color: Colors.green, size: 20)
        : const Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 20);

    final satelliteText = reading!.satelliteCount != null
        ? 'Satellites: ${reading!.satelliteCount}'
        : 'Satellites: N/A';

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        statusIcon,
        const SizedBox(width: 6),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Accuracy: ${reading!.accuracyMetres.toStringAsFixed(1)} m',
              style: TextStyle(
                color: accuracyColor,
                fontWeight: FontWeight.w600,
                fontSize: 13,
              ),
            ),
            Text(
              satelliteText,
              style: const TextStyle(fontSize: 12, color: Colors.black54),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAcquiring(BuildContext context) {
    return const Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: 16,
          height: 16,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
        SizedBox(width: 8),
        Text(
          'Acquiring GPS…',
          style: TextStyle(fontSize: 13, color: Colors.black54),
        ),
      ],
    );
  }
}
