import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../auth/models/session_model.dart';
import '../../database/app_database.dart';
import '../../dropdown/dropdown_service.dart';
import '../../gps/gps_service.dart';
import '../../gps/gps_state.dart';
import '../../photo/photo_service.dart';
import '../../photo/screens/camera_screen.dart';
import '../bloc/street_bloc.dart';

/// Capture form for a new or existing street record.
///
/// Mandatory fields: street_name, street_type, surface_type,
/// street_condition, at least one geotagged photo.
/// Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
class StreetFormScreen extends StatefulWidget {
  final SessionModel session;
  final Street? existingStreet;

  const StreetFormScreen({
    super.key,
    required this.session,
    this.existingStreet,
  });

  @override
  State<StreetFormScreen> createState() => _StreetFormScreenState();
}

class _StreetFormScreenState extends State<StreetFormScreen> {
  final _formKey = GlobalKey<FormState>();

  final _streetNameCtrl = TextEditingController();
  final _streetAddressCtrl = TextEditingController();
  String? _streetType;
  String? _surfaceType;
  String? _streetCondition;
  final _notesCtrl = TextEditingController();

  GpsPositionReading? _gpsReading;
  final List<int> _photoLocalIds = [];
  bool _isCapturingGps = false;

  // Dropdown options — loaded from DropdownService (falls back to empty list).
  List<String> _streetTypes = [];
  List<String> _surfaceTypes = [];
  List<String> _conditions = [];

  @override
  void initState() {
    super.initState();
    if (widget.existingStreet != null) {
      final s = widget.existingStreet!;
      _streetNameCtrl.text = s.streetName;
      _streetAddressCtrl.text = s.streetAddress;
      _streetType = s.streetType;
      _surfaceType = s.surfaceType;
      _streetCondition = s.streetCondition;
      _notesCtrl.text = s.notes ?? '';
    }
    _loadDropdowns();
  }

  Future<void> _loadDropdowns() async {
    final svc = context.read<DropdownService>();
    final types = await svc.streetTypes;
    final surfaces = await svc.surfaceTypes;
    final conds = await svc.streetConditions;
    if (mounted) {
      setState(() {
        _streetTypes = types.map((o) => o.label).toList();
        _surfaceTypes = surfaces.map((o) => o.label).toList();
        _conditions = conds.map((o) => o.label).toList();
      });
    }
  }

  @override
  void dispose() {
    _streetNameCtrl.dispose();
    _streetAddressCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.existingStreet == null ? 'New Street' : 'Edit Street'),
      ),
      body: BlocListener<StreetBloc, StreetState>(
        listener: _onBlocState,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildTextField(_streetNameCtrl, 'Street Name *'),
                const SizedBox(height: 12),
                _buildTextField(_streetAddressCtrl, 'Street Address *'),
                const SizedBox(height: 12),
                _buildDropdown('Street Type *', _streetTypes, _streetType,
                    (v) => setState(() => _streetType = v)),
                const SizedBox(height: 12),
                _buildDropdown('Surface Type *', _surfaceTypes, _surfaceType,
                    (v) => setState(() => _surfaceType = v)),
                const SizedBox(height: 12),
                _buildDropdown('Street Condition *', _conditions,
                    _streetCondition,
                    (v) => setState(() => _streetCondition = v)),
                const SizedBox(height: 12),
                _buildTextField(_notesCtrl, 'Notes', required: false),
                const SizedBox(height: 16),
                _buildGpsSection(),
                const SizedBox(height: 16),
                _buildPhotoSection(),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: _onSave,
                  icon: const Icon(Icons.save),
                  label: const Text('Save Street'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _onBlocState(BuildContext context, StreetState state) {
    if (state is StreetValidationError) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(
            'Missing required fields: ${state.missingFields.join(', ')}'),
        backgroundColor: Colors.red,
      ));
    } else if (state is StreetSaved) {
      _showStreetSavedDialog(context, state.street.streetId);
    } else if (state is StreetError) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(state.message),
        backgroundColor: Colors.red,
      ));
    }
  }

  void _showStreetSavedDialog(BuildContext context, String streetId) {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogCtx) => AlertDialog(
        title: const Text('Street Saved'),
        content: SingleChildScrollView(
          child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text('Street recorded successfully. Scan or print this QR code to attach to the street sign.'),
                const SizedBox(height: 16),
                Center(
                  child: SizedBox(
                    width: 200,
                    height: 200,
                    child: QrImageView(
                      data: streetId,
                      version: QrVersions.auto,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Text('Street ID:', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: Colors.grey.shade300),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: SelectableText(
                          streetId,
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.copy, size: 18),
                        tooltip: 'Copy Street ID',
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        onPressed: () {
                          Clipboard.setData(ClipboardData(text: streetId));
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Street ID copied to clipboard'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Use this ID when recording buildings on this street.',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(dialogCtx).pop();
              Navigator.of(context).pop();
            },
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }

  void _onSave() {
    if (_gpsReading == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Please capture GPS location first'),
        backgroundColor: Colors.orange,
      ));
      return;
    }

    // Build a minimal WKB LineString from the single GPS point.
    final wkb = _buildWkbLineString(_gpsReading!.longitude, _gpsReading!.latitude);

    context.read<StreetBloc>().add(SaveStreet(StreetFormData(
          streetName: _streetNameCtrl.text.trim(),
          streetAddress: _streetAddressCtrl.text.trim(),
          streetType: _streetType ?? '',
          surfaceType: _surfaceType ?? '',
          streetCondition: _streetCondition ?? '',
          notes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
          geometryWkb: wkb,
          gpsAccuracyM: _gpsReading!.accuracyMetres,
          photoLocalIds: List.from(_photoLocalIds),
          lgaCode: widget.session.lgaCode ?? '',
          enumeratorId: widget.session.userId,
        )));
  }

  Widget _buildTextField(TextEditingController ctrl, String label,
      {bool required = true}) {
    return TextFormField(
      controller: ctrl,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
      ),
      validator: required
          ? (v) => (v == null || v.trim().isEmpty) ? 'Required' : null
          : null,
    );
  }

  Widget _buildDropdown(String label, List<String> items, String? value,
      ValueChanged<String?> onChanged) {
    return DropdownButtonFormField<String>(
      value: value,
      decoration: InputDecoration(
          labelText: label, border: const OutlineInputBorder()),
      items: items
          .map((e) => DropdownMenuItem(value: e, child: Text(e)))
          .toList(),
      onChanged: onChanged,
    );
  }

  Widget _buildGpsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('GPS Location *',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (_gpsReading != null) ...[
              Text('Lat: ${_gpsReading!.latitude}'),
              Text('Lon: ${_gpsReading!.longitude}'),
              Text('Accuracy: ${_gpsReading!.accuracyMetres.toStringAsFixed(1)} m'),
              if (_gpsReading!.isLowAccuracy)
                const Text('⚠ Low accuracy — record will be flagged',
                    style: TextStyle(color: Colors.orange)),
            ] else
              const Text('No GPS fix yet'),
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: _isCapturingGps ? null : _captureGps,
              icon: _isCapturingGps
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.gps_fixed),
              label: Text(_isCapturingGps ? 'Acquiring…' : 'Capture GPS'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _captureGps() async {
    setState(() => _isCapturingGps = true);
    try {
      final gpsService = context.read<GpsService>();
      final position = await gpsService.getCurrentPosition();
      setState(() => _gpsReading = position);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('GPS error: $e')));
      }
    } finally {
      if (mounted) setState(() => _isCapturingGps = false);
    }
  }

  Widget _buildPhotoSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Photos * (at least one required)',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('${_photoLocalIds.length} photo(s) captured'),
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: _gpsReading == null ? null : _capturePhoto,
              icon: const Icon(Icons.camera_alt),
              label: const Text('Take Photo'),
            ),
            if (_gpsReading == null)
              const Text('Capture GPS first to enable photo',
                  style: TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Future<void> _capturePhoto() async {
    final xFile = await Navigator.push<XFile>(
      context,
      MaterialPageRoute(builder: (_) => const CameraScreen()),
    );
    if (xFile == null || !mounted) return;

    try {
      final photoService = context.read<PhotoService>();
      final result = await photoService.storeXFile(
        xFile: xFile,
        gpsReading: _gpsReading!,
        recordType: 'street',
        recordLocalId: 0,
        isFrontage: false,
      );
      setState(() => _photoLocalIds.add(result.localId));
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Photo captured')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Photo error: $e')));
      }
    }
  }

  /// Builds a minimal WKB LineString with a single point for the GPS fix.
  ///
  /// WKB layout (little-endian):
  ///   1 byte  — byte order (0x01 = little-endian)
  ///   4 bytes — geometry type (2 = LineString)
  ///   4 bytes — numPoints (1)
  ///   8 bytes — X (longitude)
  ///   8 bytes — Y (latitude)
  ///   Total: 25 bytes
  List<int> _buildWkbLineString(double lon, double lat) {
    final bd = ByteData(25);
    bd.setUint8(0, 1); // little-endian
    bd.setUint32(1, 2, Endian.little); // LineString
    bd.setUint32(5, 1, Endian.little); // numPoints = 1
    bd.setFloat64(9, lon, Endian.little);
    bd.setFloat64(17, lat, Endian.little);
    return bd.buffer.asUint8List().toList();
  }
}
