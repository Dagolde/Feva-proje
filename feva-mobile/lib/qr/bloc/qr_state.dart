part of 'qr_bloc.dart';

abstract class QrState extends Equatable {
  const QrState();
  @override
  List<Object?> get props => [];
}

class QrInitial extends QrState {
  const QrInitial();
}

class QrLoading extends QrState {
  const QrLoading();
}

class QrSubmitting extends QrState {
  const QrSubmitting();
}

/// Building found in local SQLite DB.
class QrBuildingFound extends QrState {
  final Building building;
  const QrBuildingFound(this.building);
  @override
  List<Object?> get props => [building];
}

/// Building found on server (not in local DB).
class QrBuildingFoundRemote extends QrState {
  final Map<String, dynamic> data;
  const QrBuildingFoundRemote(this.data);
  @override
  List<Object?> get props => [data];
}

/// Street found in local SQLite DB.
class QrStreetFound extends QrState {
  final Street street;
  const QrStreetFound(this.street);
  @override
  List<Object?> get props => [street];
}

/// Street found on server (not in local DB).
class QrStreetFoundRemote extends QrState {
  final Map<String, dynamic> data;
  const QrStreetFoundRemote(this.data);
  @override
  List<Object?> get props => [data];
}

class QrNotFound extends QrState {
  final String message;
  const QrNotFound(this.message);
  @override
  List<Object?> get props => [message];
}

class QrActionSuccess extends QrState {
  final String action; // 'verified' | 'disputed'
  const QrActionSuccess(this.action);
  @override
  List<Object?> get props => [action];
}

class QrError extends QrState {
  final String message;
  const QrError(this.message);
  @override
  List<Object?> get props => [message];
}
