import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:drift/drift.dart' show Value;
import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../database/app_database.dart';
import '../models/session_model.dart';
import '../repositories/auth_repository.dart';

part 'auth_event.dart';
part 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;
  final AppDatabase _db;

  AuthBloc({
    required AuthRepository authRepository,
    required AppDatabase db,
  })  : _authRepository = authRepository,
        _db = db,
        super(AuthInitial()) {
    on<AuthLoginRequested>(_onLoginRequested);
    on<AuthLogoutRequested>(_onLogoutRequested);
    on<AuthSessionChecked>(_onSessionChecked);
  }

  Future<void> _onLoginRequested(
    AuthLoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    try {
      print('DEBUG: Attempting login for user: ${event.username}');
      final data = await _authRepository.login(
        event.username,
        event.password,
        totpCode: event.totpCode,
      );
      print('DEBUG: Login response received: ${data.keys}');

      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String;
      final role = data['role'] as String;
      final userId = data['user_id'] as String;
      final lgaCode = data['lga_code'] as String?;
      final ward = data['ward'] as String?;
      final expiresIn = (data['expires_in'] as num?)?.toInt() ?? 28800;
      final tokenExpiresAt =
          DateTime.now().millisecondsSinceEpoch + expiresIn * 1000;

      // Hash password for offline login fallback.
      final passwordHash = sha256
          .convert(utf8.encode(event.password))
          .toString();

      print('DEBUG: Saving session to database for user: $userId');
      // Write session row to Sessions table (clear any previous session first).
      await (_db.delete(_db.sessions)).go();
      await _db.into(_db.sessions).insert(SessionsCompanion(
            userId: Value(userId),
            username: Value(event.username),
            role: Value(role),
            lgaCode: Value(lgaCode),
            ward: Value(ward),
            accessToken: Value(accessToken),
            refreshToken: Value(refreshToken),
            tokenExpiresAt: Value(tokenExpiresAt),
            createdAt: Value(DateTime.now().millisecondsSinceEpoch),
            passwordHash: Value(passwordHash),
          ));

      // Write login success to audit log.
      await _writeAuditLog(
        userId: userId,
        operation: 'login',
        detailJson: jsonEncode({'username': event.username, 'result': 'success'}),
      );

      final session = SessionModel(
        userId: userId,
        username: event.username,
        role: role,
        lgaCode: lgaCode,
        ward: ward,
        accessToken: accessToken,
        refreshToken: refreshToken,
        tokenExpiresAt: tokenExpiresAt,
      );

      print('DEBUG: Emitting AuthAuthenticated state');
      emit(AuthAuthenticated(session));
    } on AuthException catch (e) {
      print('DEBUG: AuthException - code: ${e.code}, message: ${e.message}');

      // Offline fallback: if network error, try cached credentials.
      if (e.code == 'network_error') {
        final offlineSession = await _tryOfflineLogin(
          event.username,
          event.password,
        );
        if (offlineSession != null) {
          print('DEBUG: Offline login succeeded for ${event.username}');
          emit(AuthAuthenticated(offlineSession));
          return;
        }
      }

      // Write failed attempt to audit log.
      await _writeAuditLog(
        userId: event.username,
        operation: 'login',
        detailJson: jsonEncode({
          'username': event.username,
          'result': 'failure',
          'code': e.code,
        }),
      );

      if (e.code == 'account_locked') {
        emit(AuthLocked());
      } else if (e.code == 'totp_required') {
        emit(AuthError(e.message, code: e.code));
      } else {
        emit(AuthError(e.message, code: e.code));
      }
    } catch (e, stackTrace) {
      print('DEBUG: Unexpected error during login: $e');
      print('DEBUG: Stack trace: $stackTrace');
      emit(AuthError('An unexpected error occurred: $e', code: 'unknown_error'));
    }
  }

  /// Attempts offline login by checking cached credentials in the local DB.
  /// Returns a [SessionModel] if credentials match, null otherwise.
  Future<SessionModel?> _tryOfflineLogin(
    String username,
    String password,
  ) async {
    try {
      final sessionRows = await (_db.select(_db.sessions)
            ..where((t) => t.username.equals(username)))
          .get();

      if (sessionRows.isEmpty) return null;

      final session = sessionRows.first;
      if (session.passwordHash == null) return null;

      final inputHash = sha256.convert(utf8.encode(password)).toString();
      if (inputHash != session.passwordHash) return null;

      return SessionModel(
        userId: session.userId,
        username: session.username,
        role: session.role,
        lgaCode: session.lgaCode,
        ward: session.ward,
        accessToken: session.accessToken,
        refreshToken: session.refreshToken,
        tokenExpiresAt: session.tokenExpiresAt,
      );
    } catch (_) {
      return null;
    }
  }

  Future<void> _onLogoutRequested(
    AuthLogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    try {
      // Read session from database
      final sessionRows = await _db.select(_db.sessions).get();
      if (sessionRows.isNotEmpty) {
        final session = sessionRows.first;
        final refreshToken = session.refreshToken;
        final accessToken = session.accessToken;
        final userId = session.userId;

        await _authRepository.logout(refreshToken, accessToken);

        // Write logout to audit log before clearing.
        await _writeAuditLog(
          userId: userId,
          operation: 'logout',
          detailJson: jsonEncode({'result': 'success'}),
        );
      }

      // Clear session from DB.
      await (_db.delete(_db.sessions)).go();
    } catch (_) {
      // Best-effort logout.
    }

    emit(AuthInitial());
  }

  Future<void> _onSessionChecked(
    AuthSessionChecked event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    // Read session from database
    final sessionRows = await _db.select(_db.sessions).get();
    if (sessionRows.isEmpty) {
      emit(AuthInitial());
      return;
    }

    final session = sessionRows.first;
    final tokenExpiresAt = session.tokenExpiresAt;

    // If lgaCode is missing (old session pre-dating the lgaCode column),
    // force re-login so the user gets a fresh session with lgaCode populated.
    final needsRelogin = session.lgaCode == null &&
        (session.role == 'enumerator' || session.role == 'supervisor');

    if (needsRelogin) {
      await (_db.delete(_db.sessions)).go();
      emit(AuthInitial());
      return;
    }
    
    if (tokenExpiresAt > DateTime.now().millisecondsSinceEpoch) {
      final sessionModel = SessionModel(
        userId: session.userId,
        username: session.username,
        role: session.role,
        lgaCode: session.lgaCode,
        ward: session.ward,
        accessToken: session.accessToken,
        refreshToken: session.refreshToken,
        tokenExpiresAt: tokenExpiresAt,
      );
      emit(AuthAuthenticated(sessionModel));
    } else {
      // Token expired, clear session
      await (_db.delete(_db.sessions)).go();
      emit(AuthInitial());
    }
  }

  Future<void> _writeAuditLog({
    required String userId,
    required String operation,
    String? detailJson,
  }) async {
    try {
      await _db.into(_db.auditLog).insert(AuditLogCompanion(
            userId: Value(userId),
            operation: Value(operation),
            detailJson: Value(detailJson),
            occurredAt: Value(DateTime.now().millisecondsSinceEpoch),
          ));
    } catch (_) {
      // Audit log write failure must not break auth flow.
    }
  }
}
