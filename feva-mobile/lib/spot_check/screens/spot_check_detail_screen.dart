import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../database/app_database.dart';
import '../bloc/spot_check_bloc.dart';

/// Displays full record details and allows approve / reject.
///
/// Requirements: 12.2, 12.3, 12.4, 12.5
class SpotCheckDetailScreen extends StatefulWidget {
  final SpotCheckRecord record;

  const SpotCheckDetailScreen({super.key, required this.record});

  @override
  State<SpotCheckDetailScreen> createState() => _SpotCheckDetailScreenState();
}

class _SpotCheckDetailScreenState extends State<SpotCheckDetailScreen> {
  final _rejectionController = TextEditingController();
  Map<String, dynamic>? _fullRecord;
  bool _loading = true;
  String? _loadError;
  String _verificationStatus = 'pending'; // refreshed from DB on load

  @override
  void initState() {
    super.initState();
    _loadFullRecord();
  }

  @override
  void dispose() {
    _rejectionController.dispose();
    super.dispose();
  }

  Future<void> _loadFullRecord() async {
    try {
      final db = context.read<AppDatabase>();
      if (widget.record.entityType == 'building') {
        final b = await (db.select(db.buildings)
              ..where((t) => t.id.equals(widget.record.localId)))
            .getSingleOrNull();
        if (b != null) {
          setState(() {
            _verificationStatus = b.verificationStatus.trim().toLowerCase();
            _fullRecord = {
              'Building ID': b.buildingId,
              'Street ID': b.streetId,
              'Type': b.buildingType,
              'Floors': b.numberOfFloors,
              'Units': b.numberOfUnits,
              'Condition': b.buildingCondition,
              'Has Signage': b.hasSignage == 1 ? 'Yes' : 'No',
              'Business Names': b.businessNames ?? '—',
              'LGA': b.lga,
              'Zone': b.zone ?? '—',
              'Ward': b.ward ?? '—',
              'Postcode': b.postcode ?? '—',
              'Postcode Status': b.postcodeStatus ?? '—',
              'GPS Accuracy (m)': b.gpsAccuracyM,
              'GPS Accuracy Flag': b.gpsAccuracyFlag == 1 ? 'Yes' : 'No',
              'Boundary Flag': b.boundaryFlag == 1 ? 'Yes' : 'No',
              'Duplicate Flag': b.duplicateFlag == 1 ? 'Yes' : 'No',
              'QA Flags': b.qaFlags ?? '—',
              'Enumerator': b.enumeratorId,
              'Sync Status': b.syncStatus ?? '—',
              'Notes': b.notes ?? '—',
            };
            _loading = false;
          });
        }
      } else {
        final s = await (db.select(db.streets)
              ..where((t) => t.id.equals(widget.record.localId)))
            .getSingleOrNull();
        if (s != null) {
          setState(() {
            _verificationStatus = s.verificationStatus.trim().toLowerCase();
            _fullRecord = {
              'Street ID': s.streetId,
              'Name': s.streetName,
              'Type': s.streetType,
              'Surface': s.surfaceType,
              'Condition': s.streetCondition,
              'LGA': s.lga,
              'Zone': s.zone ?? '—',
              'Ward': s.ward ?? '—',
              'GPS Accuracy Flag': s.gpsAccuracyFlag == 1 ? 'Yes' : 'No',
              'Boundary Flag': s.boundaryFlag == 1 ? 'Yes' : 'No',
              'QA Flags': s.qaFlags ?? '—',
              'Enumerator': s.enumeratorId,
              'Sync Status': s.syncStatus ?? '—',
              'Notes': s.notes ?? '—',
            };
            _loading = false;
          });
        }
      }
    } catch (e) {
      setState(() {
        _loadError = 'Failed to load record: $e';
        _loading = false;
      });
    }
  }

  void _showRejectDialog() {
    _rejectionController.clear();
    showDialog(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: const Text('Reject Record'),
        content: TextField(
          controller: _rejectionController,
          decoration: const InputDecoration(
            labelText: 'Rejection reason (required)',
            border: OutlineInputBorder(),
          ),
          maxLines: 3,
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogCtx).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () {
              final reason = _rejectionController.text.trim();
              if (reason.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                      content: Text('Rejection reason cannot be empty.')),
                );
                return;
              }
              Navigator.of(dialogCtx).pop();
              context.read<SpotCheckBloc>().add(RejectRecord(
                    entityType: widget.record.entityType,
                    localId: widget.record.localId,
                    rejectionReason: reason,
                  ));
            },
            child: const Text('Reject',
                style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<SpotCheckBloc, SpotCheckState>(
      listener: (context, state) {
        if (state is SpotCheckActionSuccess) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Text('Record ${state.action} successfully.'),
                backgroundColor: Colors.green),
          );
          Navigator.of(context).pop();
        } else if (state is SpotCheckError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Text(state.message), backgroundColor: Colors.red),
          );
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.record.recordId),
        ),
        body: BlocBuilder<SpotCheckBloc, SpotCheckState>(
          builder: (context, state) {
            if (state is SpotCheckSubmitting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (_loading) {
              return const Center(child: CircularProgressIndicator());
            }
            if (_loadError != null) {
              return Center(
                  child: Text(_loadError!,
                      style: const TextStyle(color: Colors.red)));
            }
            if (_fullRecord == null) {
              return const Center(child: Text('Record not found.'));
            }
            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _StatusBanner(status: _verificationStatus),
                const SizedBox(height: 16),
                ..._fullRecord!.entries.map(
                  (e) => _DetailRow(label: e.key, value: '${e.value}'),
                ),
                if (_verificationStatus == 'pending') ...[
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.check),
                          label: const Text('Approve'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                          onPressed: () {
                            context.read<SpotCheckBloc>().add(ApproveRecord(
                                  entityType: widget.record.entityType,
                                  localId: widget.record.localId,
                                ));
                          },
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.close),
                          label: const Text('Reject'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                          onPressed: _showRejectDialog,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                ],
              ],
            );
          },
        ),
      ),
    );
  }
}

class _StatusBanner extends StatelessWidget {
  final String status;
  const _StatusBanner({required this.status});

  @override
  Widget build(BuildContext context) {
    Color color;
    IconData icon;
    switch (status) {
      case 'approved':
        color = Colors.green;
        icon = Icons.check_circle;
        break;
      case 'rejected':
        color = Colors.red;
        icon = Icons.cancel;
        break;
      default:
        color = Colors.orange;
        icon = Icons.pending;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        border: Border.all(color: color),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, color: color),
          const SizedBox(width: 8),
          Text(
            'Status: $status',
            style: TextStyle(
                color: color, fontWeight: FontWeight.bold, fontSize: 16),
          ),
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;
  const _DetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 160,
            child: Text(label,
                style: const TextStyle(
                    fontWeight: FontWeight.w600, color: Colors.black54)),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
