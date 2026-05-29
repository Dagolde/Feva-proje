import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../bloc/qr_bloc.dart';

/// Displays building or street record for Supervisor confirmation or dispute.
///
/// Requirements: 17.3, 17.4, 17.5
class QrDetailScreen extends StatefulWidget {
  const QrDetailScreen({super.key});

  @override
  State<QrDetailScreen> createState() => _QrDetailScreenState();
}

class _QrDetailScreenState extends State<QrDetailScreen> {
  final _disputeController = TextEditingController();

  @override
  void dispose() {
    _disputeController.dispose();
    super.dispose();
  }

  // Returns (entityId, isStreet)
  (String?, bool) _entityInfo(QrState state) {
    if (state is QrBuildingFound) return (state.building.buildingId, false);
    if (state is QrBuildingFoundRemote) return (state.data['building_id'] as String?, false);
    if (state is QrStreetFound) return (state.street.streetId, true);
    if (state is QrStreetFoundRemote) return (state.data['street_id'] as String?, true);
    return (null, false);
  }

  Map<String, String> _buildDetails(QrState state) {
    if (state is QrBuildingFound) {
      final b = state.building;
      return {
        'Building ID': b.buildingId,
        'Street ID': b.streetId,
        'Type': b.buildingType,
        'Floors': '${b.numberOfFloors}',
        'Units': '${b.numberOfUnits}',
        'Condition': b.buildingCondition,
        'LGA': b.lga,
        'Ward': b.ward ?? '—',
        'Status': b.verificationStatus ?? 'pending',
      };
    }
    if (state is QrBuildingFoundRemote) {
      return state.data.map((k, v) => MapEntry(k, '$v'));
    }
    if (state is QrStreetFound) {
      final s = state.street;
      return {
        'Street ID': s.streetId,
        'Street Name': s.streetName,
        'Type': s.streetType,
        'Surface': s.surfaceType,
        'Condition': s.streetCondition,
        'LGA': s.lga,
        'Ward': s.ward ?? '—',
        'Status': s.verificationStatus ?? 'pending',
      };
    }
    if (state is QrStreetFoundRemote) {
      return state.data.map((k, v) => MapEntry(k, '$v'));
    }
    return {};
  }

  void _showDisputeDialog(BuildContext context, String entityId, bool isStreet) {
    _disputeController.clear();
    showDialog(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: Text('Dispute ${isStreet ? 'Street' : 'Building'}'),
        content: TextField(
          controller: _disputeController,
          decoration: const InputDecoration(
            labelText: 'Dispute reason (required)',
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
            style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
            onPressed: () {
              final reason = _disputeController.text.trim();
              if (reason.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Dispute reason cannot be empty.')),
                );
                return;
              }
              Navigator.of(dialogCtx).pop();
              if (isStreet) {
                context.read<QrBloc>().add(DisputeStreet(
                      streetId: entityId,
                      disputeReason: reason,
                    ));
              } else {
                context.read<QrBloc>().add(DisputeBuilding(
                      buildingId: entityId,
                      disputeReason: reason,
                    ));
              }
            },
            child: const Text('Submit', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<QrBloc, QrState>(
      listener: (context, state) {
        if (state is QrActionSuccess) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Record ${state.action} successfully.'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.of(context).pop();
        } else if (state is QrError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(state.message), backgroundColor: Colors.red),
          );
        }
      },
      builder: (context, state) {
        if (state is QrSubmitting) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }

        final (entityId, isStreet) = _entityInfo(state);
        final details = _buildDetails(state);
        final title = isStreet
            ? 'Street: ${entityId ?? '—'}'
            : 'Building: ${entityId ?? '—'}';

        return Scaffold(
          appBar: AppBar(
            title: Text(title),
            actions: [
              if (entityId != null) ...[
                TextButton.icon(
                  icon: const Icon(Icons.verified, color: Colors.white),
                  label: const Text('Verify', style: TextStyle(color: Colors.white)),
                  onPressed: () {
                    if (isStreet) {
                      context.read<QrBloc>().add(VerifyStreet(entityId));
                    } else {
                      context.read<QrBloc>().add(VerifyBuilding(entityId));
                    }
                  },
                ),
                TextButton.icon(
                  icon: const Icon(Icons.report_problem, color: Colors.white),
                  label: const Text('Dispute', style: TextStyle(color: Colors.white)),
                  onPressed: () => _showDisputeDialog(context, entityId, isStreet),
                ),
              ],
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Entity type chip
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Chip(
                  avatar: Icon(
                    isStreet ? Icons.add_road : Icons.apartment,
                    size: 16,
                  ),
                  label: Text(isStreet ? 'Street Record' : 'Building Record'),
                  backgroundColor: isStreet
                      ? Colors.blue.shade50
                      : Colors.green.shade50,
                ),
              ),
              ...details.entries.map((e) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 6),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(
                          width: 160,
                          child: Text(e.key,
                              style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                  color: Colors.black54)),
                        ),
                        Expanded(child: Text(e.value)),
                      ],
                    ),
                  )),
            ],
          ),
        );
      },
    );
  }
}
