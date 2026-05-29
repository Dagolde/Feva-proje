/// Central configuration for the FEVA mobile app.
///
/// Change [backendBaseUrl] to match your server's IP/hostname.
/// - For Android emulator connecting to localhost: http://10.0.2.2:8000
/// - For physical device on same Wi-Fi: http://<your-machine-ip>:8000
/// - For production: https://api.yourdomain.com
class AppConfig {
  AppConfig._();

  /// Base URL of the FEVA backend API.
  static const String backendBaseUrl = 'http://192.168.1.106:8000';
}
