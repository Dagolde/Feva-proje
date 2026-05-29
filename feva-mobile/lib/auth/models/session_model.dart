import 'package:equatable/equatable.dart';

class SessionModel extends Equatable {
  final String userId;
  final String username;
  final String role;
  final String? lgaCode;
  final String? ward;
  final String accessToken;
  final String refreshToken;
  final int tokenExpiresAt; // Unix epoch ms

  const SessionModel({
    required this.userId,
    required this.username,
    required this.role,
    this.lgaCode,
    this.ward,
    required this.accessToken,
    required this.refreshToken,
    required this.tokenExpiresAt,
  });

  bool get isExpired =>
      tokenExpiresAt <= DateTime.now().millisecondsSinceEpoch;

  @override
  List<Object?> get props =>
      [userId, username, role, lgaCode, ward, accessToken, refreshToken, tokenExpiresAt];
}
