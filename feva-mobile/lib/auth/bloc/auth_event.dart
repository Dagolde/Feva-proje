part of 'auth_bloc.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class AuthLoginRequested extends AuthEvent {
  final String username;
  final String password;
  final String? totpCode;

  const AuthLoginRequested({
    required this.username,
    required this.password,
    this.totpCode,
  });

  @override
  List<Object?> get props => [username, password, totpCode];
}

class AuthLogoutRequested extends AuthEvent {
  const AuthLogoutRequested();
}

/// Emitted on app start to check whether a valid stored session exists.
class AuthSessionChecked extends AuthEvent {
  const AuthSessionChecked();
}
