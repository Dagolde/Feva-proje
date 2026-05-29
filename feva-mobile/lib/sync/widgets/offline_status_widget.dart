import 'package:drift/drift.dart' show Value, countAll;
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../database/app_database.dart';
import '../sync_engine.dart';
import '../sync_status_event.dart';

/// Displays the count of unsynced records and a manual sync trigger button.
///
/// Subscribes to `SELECT COUNT(*) FROM sync_queue WHERE status='pending'`
/// via a Drift watch query for real-time updates.
///
/// Requirements: 6.4, 6.6
class OfflineStatusWidget extends StatefulWidget {
  /// The sync engine used for manual trigger and status events.
  final SyncEngine syncEngine;

  const OfflineStatusWidget({super.key, required this.syncEngine});

  @override
  State<OfflineStatusWidget> createState() => _OfflineStatusWidgetState();
}

class _OfflineStatusWidgetState extends State<OfflineStatusWidget> {
  bool _isSyncing = false;
  String? _lastSyncMessage;

  @override
  void initState() {
    super.initState();
    widget.syncEngine.statusStream.listen(_onSyncEvent);
  }

  void _onSyncEvent(SyncStatusEvent event) {
    if (!mounted) return;
    setState(() {
      switch (event) {
        case SyncStarted():
          _isSyncing = true;
          _lastSyncMessage = 'Syncing ${event.pendingCount} record(s)…';
        case SyncCompleted():
          _isSyncing = false;
          _lastSyncMessage =
              '✓ ${event.accepted} synced, ${event.rejected} failed';
        case SyncFailed():
          _isSyncing = false;
          _lastSyncMessage = '✗ ${event.message}';
        default:
          break;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final db = context.read<AppDatabase>();

    return StreamBuilder<int>(
      stream: _pendingCountStream(db),
      builder: (context, snapshot) {
        final count = snapshot.data ?? 0;

        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: count > 0 ? Colors.orange.shade100 : Colors.green.shade100,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                count > 0 ? Icons.cloud_upload_outlined : Icons.cloud_done,
                size: 18,
                color: count > 0 ? Colors.orange.shade800 : Colors.green.shade800,
              ),
              const SizedBox(width: 6),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    count > 0 ? '$count unsynced' : 'All synced',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: count > 0
                          ? Colors.orange.shade900
                          : Colors.green.shade900,
                    ),
                  ),
                  if (_lastSyncMessage != null)
                    Text(
                      _lastSyncMessage!,
                      style: const TextStyle(fontSize: 11),
                    ),
                ],
              ),
              if (count > 0) ...[
                const SizedBox(width: 8),
                _isSyncing
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : IconButton(
                        icon: const Icon(Icons.sync, size: 18),
                        tooltip: 'Sync now',
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        onPressed: _triggerSync,
                      ),
              ],
            ],
          ),
        );
      },
    );
  }

  /// Returns a stream of the pending sync_queue count, updated in real time.
  Stream<int> _pendingCountStream(AppDatabase db) {
    final countExpr = countAll();
    final query = db.selectOnly(db.syncQueue)
      ..addColumns([countExpr])
      ..where(db.syncQueue.status.equals('pending'));
    return query.watchSingle().map((row) => row.read(countExpr) ?? 0);
  }

  Future<void> _triggerSync() async {
    if (_isSyncing) return;
    setState(() => _isSyncing = true);
    await widget.syncEngine.triggerManualSync();
  }
}
