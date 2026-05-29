part of 'street_bloc.dart';

abstract class StreetEvent extends Equatable {
  const StreetEvent();
  @override
  List<Object?> get props => [];
}

class LoadStreets extends StreetEvent {
  const LoadStreets();
}

class SaveStreet extends StreetEvent {
  final StreetFormData formData;
  const SaveStreet(this.formData);
  @override
  List<Object?> get props => [formData];
}

class DeleteStreet extends StreetEvent {
  final int localId;
  const DeleteStreet(this.localId);
  @override
  List<Object?> get props => [localId];
}
