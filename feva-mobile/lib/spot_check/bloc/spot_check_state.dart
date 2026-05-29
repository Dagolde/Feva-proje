part of 'spot_check_bloc.dart';

abstract class SpotCheckState extends Equatable {
  const SpotCheckState();
  @override
  List<Object?> get props => [];
}

class SpotCheckInitial extends SpotCheckState {
  const SpotCheckInitial();
}

class SpotCheckLoading extends SpotCheckState {
  const SpotCheckLoading();
}

class SpotCheckLoaded extends SpotCheckState {
  final List<SpotCheckRecord> records;
  const SpotCheckLoaded(this.records);
  @override
  List<Object?> get props => [records];
}

class SpotCheckSubmitting extends SpotCheckState {
  const SpotCheckSubmitting();
}

/// Emitted after a successful approve or reject action.
class SpotCheckActionSuccess extends SpotCheckState {
  final String action; // 'approved' | 'rejected'
  const SpotCheckActionSuccess(this.action);
  @override
  List<Object?> get props => [action];
}

class SpotCheckError extends SpotCheckState {
  final String message;
  const SpotCheckError(this.message);
  @override
  List<Object?> get props => [message];
}
