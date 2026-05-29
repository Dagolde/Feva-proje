import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../bloc/spot_check_bloc.dart';
import 'spot_check_detail_screen.dart';

/// Lists all Building/Street records in the Supervisor's assigned LGA,
/// sorted by submission date descending.
///
/// Requirements: 12.1
class SpotCheckListScreen extends StatelessWidget {
  const SpotCheckListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Spot Check'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: () =>
                context.read<SpotCheckBloc>().add(const LoadSpotCheckRecords()),
          ),
        ],
      ),
      body: BlocBuilder<SpotCheckBloc, SpotCheckState>(
        builder: (context, state) {
          if (state is SpotCheckLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state is SpotCheckError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(state.message,
                      style: const TextStyle(color: Colors.red)),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: () => context
                        .read<SpotCheckBloc>()
                        .add(const LoadSpotCheckRecords()),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }
          if (state is SpotCheckLoaded) {
            if (state.records.isEmpty) {
              return const Center(child: Text('No records to review.'));
            }
            return ListView.separated(
              itemCount: state.records.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final record = state.records[index];
                return _RecordTile(record: record);
              },
            );
          }
          return const SizedBox.shrink();
        },
      ),
    );
  }
}

class _RecordTile extends StatelessWidget {
  final SpotCheckRecord record;
  const _RecordTile({required this.record});

  @override
  Widget build(BuildContext context) {
    final dt = DateTime.fromMillisecondsSinceEpoch(record.enumerationDate);
    final date = '${dt.day.toString().padLeft(2, '0')}/'
        '${dt.month.toString().padLeft(2, '0')}/'
        '${dt.year}';

    Color statusColor;
    switch (record.verificationStatus) {
      case 'approved':
        statusColor = Colors.green;
        break;
      case 'rejected':
        statusColor = Colors.red;
        break;
      default:
        statusColor = Colors.orange;
    }

    return ListTile(
      leading: Icon(
        record.entityType == 'building' ? Icons.apartment : Icons.route,
        color: Theme.of(context).colorScheme.primary,
      ),
      title: Text(record.recordId),
      subtitle: Text(
          '${record.ward ?? record.lga} · $date · ${record.enumeratorId}'),
      trailing: Chip(
        label: Text(
          record.verificationStatus,
          style: const TextStyle(color: Colors.white, fontSize: 11),
        ),
        backgroundColor: statusColor,
        padding: EdgeInsets.zero,
      ),
      onTap: () {
        Navigator.of(context).push(MaterialPageRoute(
          builder: (_) => BlocProvider.value(
            value: context.read<SpotCheckBloc>(),
            child: SpotCheckDetailScreen(record: record),
          ),
        ));
      },
    );
  }
}
