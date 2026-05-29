part of 'qr_bloc.dart';

abstract class QrEvent extends Equatable {
  const QrEvent();
  @override
  List<Object?> get props => [];
}

class ScanQrCode extends QrEvent {
  final String qrValue;
  const ScanQrCode(this.qrValue);
  @override
  List<Object?> get props => [qrValue];
}

class VerifyBuilding extends QrEvent {
  final String buildingId;
  const VerifyBuilding(this.buildingId);
  @override
  List<Object?> get props => [buildingId];
}

class DisputeBuilding extends QrEvent {
  final String buildingId;
  final String disputeReason;
  const DisputeBuilding({required this.buildingId, required this.disputeReason});
  @override
  List<Object?> get props => [buildingId, disputeReason];
}

class VerifyStreet extends QrEvent {
  final String streetId;
  const VerifyStreet(this.streetId);
  @override
  List<Object?> get props => [streetId];
}

class DisputeStreet extends QrEvent {
  final String streetId;
  final String disputeReason;
  const DisputeStreet({required this.streetId, required this.disputeReason});
  @override
  List<Object?> get props => [streetId, disputeReason];
}
