part of 'auth_bloc.dart';

abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

/// Initial state — no session loaded yet.
class AuthInitial extends AuthState {}

/// Authentication request in progress.
class AuthLoading extends AuthState {}

/// User is authenticated with a valid session.
class AuthAuthenticated extends AuthState {
  final SessionModel session;

  const AuthAuthenticated(this.session);

  @override
  List<Object?> get props => [session];
}

/// Authentication failed with an error message.
class AuthError extends AuthState {
  final String message;

  /// Optional machine-readable code, e.g. 'totp_required', 'invalid_credentials'.
  final String? code;

  const AuthError(this.message, {this.code});

  @override
  List<Object?> get props => [message, code];
}

/// Account is locked after too many failed attempts.
class AuthLocked extends AuthState {}
