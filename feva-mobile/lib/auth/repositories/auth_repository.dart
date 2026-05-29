import 'dart:convert';
import 'package:http/http.dart' as http;

import '../../core/app_config.dart';

/// Thrown when an auth operation fails.
class AuthException implements Exception {
  /// One of: 'invalid_credentials', 'account_locked', 'totp_required',
  /// 'network_error'
  final String code;
  final String message;

  const AuthException({required this.code, required this.message});

  @override
  String toString() => 'AuthException($code): $message';
}

class AuthRepository {
  final http.Client _client;

  AuthRepository({
    http.Client? client,
  })  : _client = client ?? http.Client();

  /// POST /api/v1/auth/login
  /// Returns the full response body map on success.
  /// Throws [AuthException] on failure.
  Future<Map<String, dynamic>> login(
    String username,
    String password, {
    String? totpCode,
  }) async {
    final uri = Uri.parse('${AppConfig.backendBaseUrl}/api/v1/auth/login');

    try {
      final response = await _client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
          if (totpCode != null) 'totp_code': totpCode,
        }),
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () => throw AuthException(
          code: 'network_error',
          message: 'Connection timed out. Check that the server is reachable.',
        ),
      );

      final body = jsonDecode(response.body) as Map<String, dynamic>;

      switch (response.statusCode) {
        case 200:
          return body;
        case 401:
          throw const AuthException(
            code: 'invalid_credentials',
            message: 'Invalid username or password.',
          );
        case 403:
          throw const AuthException(
            code: 'account_locked',
            message: 'Account is locked. Please contact your administrator.',
          );
        case 422:
          throw const AuthException(
            code: 'totp_required',
            message: 'Two-factor authentication code required.',
          );
        default:
          throw AuthException(
            code: 'network_error',
            message: 'Unexpected server response: ${response.statusCode}',
          );
      }
    } on AuthException {
      rethrow;
    } catch (e) {
      throw AuthException(
        code: 'network_error',
        message: 'Network error: $e',
      );
    }
  }

  /// POST /api/v1/auth/logout
  Future<void> logout(String refreshToken, String accessToken) async {
    final uri = Uri.parse('${AppConfig.backendBaseUrl}/api/v1/auth/logout');

    try {
      await _client.post(
        uri,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode({'refresh_token': refreshToken}),
      );
    } catch (_) {
      // Best-effort logout; ignore network errors.
    }
  }
}
