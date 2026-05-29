part of 'spot_check_bloc.dart';

abstract class SpotCheckEvent extends Equatable {
  const SpotCheckEvent();
  @override
  List<Object?> get props => [];
}

class LoadSpotCheckRecords extends SpotCheckEvent {
  const LoadSpotCheckRecords();
}

class ApproveRecord extends SpotCheckEvent {
  final String entityType; // 'building' | 'street'
  final int localId;
  final String? serverId;

  const ApproveRecord({
    required this.entityType,
    required this.localId,
    this.serverId,
  });

  @override
  List<Object?> get props => [entityType, localId, serverId];
}

class RejectRecord extends SpotCheckEvent {
  final String entityType;
  final int localId;
  final String? serverId;
  final String rejectionReason;

  const RejectRecord({
    required this.entityType,
    required this.localId,
    required this.rejectionReason,
    this.serverId,
  });

  @override
  List<Object?> get props => [entityType, localId, serverId, rejectionReason];
}
