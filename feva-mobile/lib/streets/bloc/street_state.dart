part of 'street_bloc.dart';

abstract class StreetState extends Equatable {
  const StreetState();
  @override
  List<Object?> get props => [];
}

class StreetInitial extends StreetState {
  const StreetInitial();
}

class StreetLoading extends StreetState {
  const StreetLoading();
}

class StreetListLoaded extends StreetState {
  final List<Street> streets;
  const StreetListLoaded(this.streets);
  @override
  List<Object?> get props => [streets];
}

class StreetSaving extends StreetState {
  const StreetSaving();
}

class StreetSaved extends StreetState {
  final Street street;
  const StreetSaved(this.street);
  @override
  List<Object?> get props => [street];
}

class StreetValidationError extends StreetState {
  /// Names of mandatory fields that are missing.
  final List<String> missingFields;
  const StreetValidationError(this.missingFields);
  @override
  List<Object?> get props => [missingFields];
}

class StreetError extends StreetState {
  final String message;
  const StreetError(this.message);
  @override
  List<Object?> get props => [message];
}
