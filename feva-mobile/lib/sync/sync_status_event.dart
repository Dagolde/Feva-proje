/// Events emitted by [SyncEngine] to the UI stream.
///
/// Requirements: 7.3, 7.4, 7.5, 7.6
sealed class SyncStatusEvent {}

/// Sync cycle started — [pendingCount] items queued.
final class SyncStarted extends SyncStatusEvent {
  final int pendingCount;
  SyncStarted(this.pendingCount);
}

/// A single record was accepted by the server.
final class SyncRecordAccepted extends SyncStatusEvent {
  final int localId;
  final String entityType;
  final String serverId;
  SyncRecordAccepted({
    required this.localId,
    required this.entityType,
    required this.serverId,
  });
}

/// A single record was rejected by the server.
final class SyncRecordRejected extends SyncStatusEvent {
  final int localId;
  final String entityType;
  final List<String> errors;
  SyncRecordRejected({
    required this.localId,
    required this.entityType,
    required this.errors,
  });
}

/// Sync cycle completed.
final class SyncCompleted extends SyncStatusEvent {
  final int accepted;
  final int rejected;
  SyncCompleted({required this.accepted, required this.rejected});
}

/// Sync cycle failed with an unrecoverable error (e.g. no token).
final class SyncFailed extends SyncStatusEvent {
  final String message;
  SyncFailed(this.message);
}
