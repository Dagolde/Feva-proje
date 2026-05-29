/// Manual coordinate entry dialog shown after a 30-second GPS timeout.
///
/// Requirement 4.6: allow manual retry or manual coordinate entry with a
/// mandatory accuracy disclaimer flag.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../gps_state.dart';

/// Dialog that lets the Enumerator enter coordinates manually when GPS times out.
///
/// Returns a [GpsPositionReading] with [isManualEntry] = true when the user
/// confirms, or `null` when the user chooses to retry GPS.
///
/// Usage:
/// ```dart
/// final result = await ManualCoordDialog.show(context);
/// if (result != null) {
///   // use manual reading
/// } else {
///   // retry GPS
/// }
/// ```
class ManualCoordDialog extends StatefulWidget {
  const ManualCoordDialog({super.key});

  /// Convenience helper to show the dialog and await the result.
  static Future<GpsPositionReading?> show(BuildContext context) =>
      showDialog<GpsPositionReading?>(
        context: context,
        barrierDismissible: false,
        builder: (_) => const ManualCoordDialog(),
      );

  @override
  State<ManualCoordDialog> createState() => _ManualCoordDialogState();
}

class _ManualCoordDialogState extends State<ManualCoordDialog> {
  final _formKey = GlobalKey<FormState>();
  final _latController = TextEditingController();
  final _lonController = TextEditingController();

  @override
  void dispose() {
    _latController.dispose();
    _lonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('GPS Timeout — Enter Coordinates Manually'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Disclaimer
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.amber.shade50,
                border: Border.all(color: Colors.amber.shade300),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text(
                '⚠ Manually entered coordinates will be flagged for '
                'Supervisor review',
                style: TextStyle(fontSize: 12, color: Colors.black87),
              ),
            ),
            const SizedBox(height: 16),

            // Latitude field
            TextFormField(
              controller: _latController,
              decoration: const InputDecoration(
                labelText: 'Latitude',
                hintText: 'e.g. 6.45123',
                border: OutlineInputBorder(),
                isDense: true,
              ),
              keyboardType: const TextInputType.numberWithOptions(
                signed: true,
                decimal: true,
              ),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[-0-9.]')),
              ],
              validator: _validateLatitude,
            ),
            const SizedBox(height: 12),

            // Longitude field
            TextFormField(
              controller: _lonController,
              decoration: const InputDecoration(
                labelText: 'Longitude',
                hintText: 'e.g. 3.39876',
                border: OutlineInputBorder(),
                isDense: true,
              ),
              keyboardType: const TextInputType.numberWithOptions(
                signed: true,
                decimal: true,
              ),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[-0-9.]')),
              ],
              validator: _validateLongitude,
            ),
          ],
        ),
      ),
      actions: [
        // Retry GPS — returns null to the caller
        TextButton(
          onPressed: () => Navigator.of(context).pop(null),
          child: const Text('Retry GPS'),
        ),

        // Confirm — validates and returns a manual GpsPositionReading
        ElevatedButton(
          onPressed: _onConfirm,
          child: const Text('Confirm'),
        ),
      ],
    );
  }

  void _onConfirm() {
    if (!_formKey.currentState!.validate()) return;

    final lat = double.parse(_latController.text.trim());
    final lon = double.parse(_lonController.text.trim());

    // Sentinel values for manual entry:
    //   accuracyMetres = 999.0  (indicates manual / unknown accuracy)
    //   isManualEntry  = true   (triggers gps_accuracy_flag=1 on the record)
    final reading = GpsPositionReading(
      latitude: lat,
      longitude: lon,
      accuracyMetres: 999.0,
      capturedAt: DateTime.now().toUtc(),
      isManualEntry: true,
    );

    Navigator.of(context).pop(reading);
  }

  String? _validateLatitude(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Latitude is required';
    }
    final parsed = double.tryParse(value.trim());
    if (parsed == null) return 'Enter a valid number';
    if (parsed < -90 || parsed > 90) return 'Latitude must be between -90 and 90';
    return null;
  }

  String? _validateLongitude(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Longitude is required';
    }
    final parsed = double.tryParse(value.trim());
    if (parsed == null) return 'Enter a valid number';
    if (parsed < -180 || parsed > 180) return 'Longitude must be between -180 and 180';
    return null;
  }
}
