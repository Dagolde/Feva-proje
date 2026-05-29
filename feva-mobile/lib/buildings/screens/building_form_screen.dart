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
import '../bloc/building_bloc.dart';

/// Capture form for a new or existing building record.
///
/// Mandatory fields: building_type, number_of_floors, number_of_units,
/// building_condition, frontage_photo, valid street_id.
/// Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9
class BuildingFormScreen extends StatefulWidget {
  final SessionModel session;
  final Building? existingBuilding;

  const BuildingFormScreen({
    super.key,
    required this.session,
    this.existingBuilding,
  });

  @override
  State<BuildingFormScreen> createState() => _BuildingFormScreenState();
}

class _BuildingFormScreenState extends State<BuildingFormScreen> {
  final _formKey = GlobalKey<FormState>();

  final _streetIdCtrl = TextEditingController();
  String? _buildingType;
  final _floorsCtrl = TextEditingController();
  final _unitsCtrl = TextEditingController();
  String? _buildingCondition;
  final _notesCtrl = TextEditingController();

  String? _streetAddress;
  final _streetAddressDisplayCtrl = TextEditingController();

  bool _hasSignage = false;
  final List<TextEditingController> _businessNameCtrls = [];

  GpsPositionReading? _gpsReading;
  int? _frontagePhotoLocalId;
  final List<int> _additionalPhotoLocalIds = [];
  bool _isCapturingGps = false;

  static const _conditions = ['Good', 'Fair', 'Poor', 'Very Poor'];

  // Dropdown options — loaded from DropdownService.
  List<String> _buildingTypes = [];
  List<String> _buildingConditions = [];

  @override
  void initState() {
    super.initState();
    if (widget.existingBuilding != null) {
      final b = widget.existingBuilding!;
      _streetIdCtrl.text = b.streetId;
      _buildingType = b.buildingType;
      _floorsCtrl.text = b.numberOfFloors.toString();
      _unitsCtrl.text = b.numberOfUnits.toString();
      _buildingCondition = b.buildingCondition;
      _notesCtrl.text = b.notes ?? '';
      _hasSignage = b.hasSignage == 1;
      _streetAddress = b.streetAddress;
      _streetAddressDisplayCtrl.text = b.streetAddress ?? '';
    }
    _loadDropdowns();
  }

  Future<void> _onStreetIdChanged(String streetId) async {
    final db = context.read<AppDatabase>();
    final street = await (db.select(db.streets)
          ..where((t) => t.streetId.equals(streetId.trim())))
        .getSingleOrNull();
    if (mounted) {
      setState(() {
        _streetAddress = street?.streetAddress;
        _streetAddressDisplayCtrl.text = _streetAddress ?? '';
      });
    }
  }

  Future<void> _loadDropdowns() async {
    final svc = context.read<DropdownService>();
    final types = await svc.buildingTypes;
    final conds = await svc.buildingConditions;
    if (mounted) {
      setState(() {
        _buildingTypes = types.map((o) => o.label).toList();
        _buildingConditions = conds.map((o) => o.label).toList();
      });
    }
  }

  @override
  void dispose() {
    _streetIdCtrl.dispose();
    _floorsCtrl.dispose();
    _unitsCtrl.dispose();
    _notesCtrl.dispose();
    _streetAddressDisplayCtrl.dispose();
    for (final c in _businessNameCtrls) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.existingBuilding == null
            ? 'New Building'
            : 'Edit Building'),
      ),
      body: BlocListener<BuildingBloc, BuildingState>(
        listener: _onBlocState,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildTextField(_streetIdCtrl, 'Street ID *',
                    hint: 'e.g. STR-LAGOS-000001',
                    onChanged: _onStreetIdChanged),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _streetAddressDisplayCtrl,
                  enabled: false,
                  decoration: const InputDecoration(
                    labelText: 'Street Address',
                    border: OutlineInputBorder(),
                    helperText: 'Auto-populated from Street ID',
                  ),
                ),
                const SizedBox(height: 12),
                _buildDropdown('Building Type *', _buildingTypes, _buildingType,
                    (v) => setState(() => _buildingType = v)),
                const SizedBox(height: 12),
                _buildNumberField(_floorsCtrl, 'Number of Floors *'),
                const SizedBox(height: 12),
                _buildNumberField(_unitsCtrl, 'Number of Units *'),
                const SizedBox(height: 12),
                _buildDropdown('Building Condition *', _buildingConditions,
                    _buildingCondition,
                    (v) => setState(() => _buildingCondition = v)),
                const SizedBox(height: 12),
                _buildTextField(_notesCtrl, 'Notes', required: false),
                const SizedBox(height: 16),
                _buildSignageSection(),
                const SizedBox(height: 16),
                _buildGpsSection(),
                const SizedBox(height: 16),
                _buildPhotoSection(),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: _onSave,
                  icon: const Icon(Icons.save),
                  label: const Text('Save Building'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _onBlocState(BuildContext context, BuildingState state) {
    if (state is BuildingValidationError) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(
            'Missing required fields: ${state.missingFields.join(', ')}'),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 4),
      ));
    } else if (state is BuildingSaved) {
      _showBuildingQrDialog(context, state.building.buildingId);
    } else if (state is BuildingError) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(state.message),
        backgroundColor: Colors.red,
      ));
    }
  }

  void _showBuildingQrDialog(BuildContext context, String buildingId) {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogCtx) => AlertDialog(
        title: const Text('Building Saved'),
        content: SingleChildScrollView(
          child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text('Record saved. Scan or print this QR code to attach to the building.'),
                const SizedBox(height: 16),
                Center(
                  child: SizedBox(
                    width: 200,
                    height: 200,
                    child: QrImageView(
                      data: buildingId,
                      version: QrVersions.auto,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Text('Building ID:', style: TextStyle(fontWeight: FontWeight.bold)),
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
                          buildingId,
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.copy, size: 18),
                        tooltip: 'Copy Building ID',
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        onPressed: () {
                          Clipboard.setData(ClipboardData(text: buildingId));
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Building ID copied'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
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

    final wkb = _buildWkbPoint(
        _gpsReading!.longitude, _gpsReading!.latitude);

    final businessNames = _businessNameCtrls
        .map((c) => c.text.trim())
        .where((s) => s.isNotEmpty)
        .toList();

    context.read<BuildingBloc>().add(SaveBuilding(BuildingFormData(
          streetId: _streetIdCtrl.text.trim(),
          buildingType: _buildingType ?? '',
          numberOfFloors: int.tryParse(_floorsCtrl.text) ?? 0,
          numberOfUnits: int.tryParse(_unitsCtrl.text) ?? 0,
          buildingCondition: _buildingCondition ?? '',
          notes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
          geometryWkb: wkb,
          gpsAccuracyM: _gpsReading!.accuracyMetres,
          frontagePhotoLocalId: _frontagePhotoLocalId,
          additionalPhotoLocalIds: List.from(_additionalPhotoLocalIds),
          hasSignage: _hasSignage,
          businessNames: businessNames,
          lgaCode: widget.session.lgaCode ?? '',
          enumeratorId: widget.session.userId,
        )));
  }

  Widget _buildTextField(TextEditingController ctrl, String label,
      {bool required = true, String? hint, ValueChanged<String>? onChanged}) {
    return TextFormField(
      controller: ctrl,
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        border: const OutlineInputBorder(),
      ),
      validator: required
          ? (v) => (v == null || v.trim().isEmpty) ? 'Required' : null
          : null,
    );
  }

  Widget _buildNumberField(TextEditingController ctrl, String label) {
    return TextFormField(
      controller: ctrl,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(
          labelText: label, border: const OutlineInputBorder()),
      validator: (v) {
        final n = int.tryParse(v ?? '');
        if (n == null || n <= 0) return 'Must be a positive number';
        return null;
      },
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

  Widget _buildSignageSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SwitchListTile(
              title: const Text('Has Signage?'),
              value: _hasSignage,
              onChanged: (v) => setState(() {
                _hasSignage = v;
                if (!v) {
                  for (final c in _businessNameCtrls) {
                    c.dispose();
                  }
                  _businessNameCtrls.clear();
                }
              }),
            ),
            if (_hasSignage) ...[
              const SizedBox(height: 8),
              const Text('Business Names',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              ..._businessNameCtrls.asMap().entries.map((entry) => Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: entry.value,
                            decoration: InputDecoration(
                              labelText: 'Business ${entry.key + 1}',
                              border: const OutlineInputBorder(),
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.remove_circle_outline),
                          onPressed: () => setState(() {
                            entry.value.dispose();
                            _businessNameCtrls.removeAt(entry.key);
                          }),
                        ),
                      ],
                    ),
                  )),
              TextButton.icon(
                onPressed: () => setState(
                    () => _businessNameCtrls.add(TextEditingController())),
                icon: const Icon(Icons.add),
                label: const Text('Add Business'),
              ),
            ],
          ],
        ),
      ),
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
              Text(
                  'Accuracy: ${_gpsReading!.accuracyMetres.toStringAsFixed(1)} m'),
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
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('GPS error: $e')));
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
            const Text('Photos',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ListTile(
              leading: Icon(
                _frontagePhotoLocalId != null
                    ? Icons.check_circle
                    : Icons.camera_front,
                color: _frontagePhotoLocalId != null
                    ? Colors.green
                    : Colors.grey,
              ),
              title: const Text('Frontage Photo *'),
              subtitle: Text(_frontagePhotoLocalId != null
                  ? 'Captured'
                  : 'Required — tap to capture'),
              onTap: _gpsReading == null ? null : _captureFrontagePhoto,
            ),
            if (_additionalPhotoLocalIds.isNotEmpty)
              Text('${_additionalPhotoLocalIds.length} additional photo(s)'),
            TextButton.icon(
              onPressed: _gpsReading == null ? null : _captureAdditionalPhoto,
              icon: const Icon(Icons.add_a_photo),
              label: const Text('Add Photo'),
            ),
            if (_gpsReading == null)
              const Text('Capture GPS first to enable photos',
                  style: TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Future<void> _captureFrontagePhoto() async {
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
        recordType: 'building',
        recordLocalId: 0,
        isFrontage: true,
      );
      setState(() => _frontagePhotoLocalId = result.localId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Frontage photo captured')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Photo error: $e')));
      }
    }
  }

  Future<void> _captureAdditionalPhoto() async {
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
        recordType: 'building',
        recordLocalId: 0,
        isFrontage: false,
      );
      setState(() => _additionalPhotoLocalIds.add(result.localId));
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

  /// Builds a WKB Point (little-endian) from [lon] and [lat].
  ///
  /// WKB layout: byteOrder(1) + wkbType(4) + X(8) + Y(8) = 21 bytes
  List<int> _buildWkbPoint(double lon, double lat) {
    final bd = ByteData(21);
    bd.setUint8(0, 1); // little-endian
    bd.setUint32(1, 1, Endian.little); // Point
    bd.setFloat64(5, lon, Endian.little);
    bd.setFloat64(13, lat, Endian.little);
    return bd.buffer.asUint8List().toList();
  }
}
