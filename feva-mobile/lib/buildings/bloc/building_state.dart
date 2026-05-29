part of 'building_bloc.dart';

abstract class BuildingState extends Equatable {
  const BuildingState();
  @override
  List<Object?> get props => [];
}

class BuildingInitial extends BuildingState {
  const BuildingInitial();
}

class BuildingLoading extends BuildingState {
  const BuildingLoading();
}

class BuildingListLoaded extends BuildingState {
  final List<Building> buildings;
  const BuildingListLoaded(this.buildings);
  @override
  List<Object?> get props => [buildings];
}

class BuildingSaving extends BuildingState {
  const BuildingSaving();
}

class BuildingSaved extends BuildingState {
  final Building building;
  const BuildingSaved(this.building);
  @override
  List<Object?> get props => [building];
}

class BuildingValidationError extends BuildingState {
  /// Human-readable names of missing/invalid mandatory fields.
  final List<String> missingFields;
  const BuildingValidationError(this.missingFields);
  @override
  List<Object?> get props => [missingFields];
}

class BuildingError extends BuildingState {
  final String message;
  const BuildingError(this.message);
  @override
  List<Object?> get props => [message];
}
