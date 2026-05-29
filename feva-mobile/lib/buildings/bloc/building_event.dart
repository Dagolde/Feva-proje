part of 'building_bloc.dart';

abstract class BuildingEvent extends Equatable {
  const BuildingEvent();
  @override
  List<Object?> get props => [];
}

class LoadBuildings extends BuildingEvent {
  const LoadBuildings();
}

class SaveBuilding extends BuildingEvent {
  final BuildingFormData formData;
  const SaveBuilding(this.formData);
  @override
  List<Object?> get props => [formData];
}

class DeleteBuilding extends BuildingEvent {
  final int localId;
  const DeleteBuilding(this.localId);
  @override
  List<Object?> get props => [localId];
}
