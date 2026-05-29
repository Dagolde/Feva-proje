import 'dart:async';
import 'dart:io';

/// Monitors network connectivity by attempting a DNS lookup.
///
/// Requirements: 9.1, 9.2, 9.3
class ConnectivityService {
  static const _checkHost = 'api.feva.igsl.com';
  static const _checkInterval = Duration(seconds: 30);

  final _controller = StreamController<bool>.broadcast();
  Timer? _timer;
  bool _isOnline = false;

  /// Stream of connectivity state changes (true = online, false = offline).
  Stream<bool> get onConnectivityChanged => _controller.stream;

  bool get isOnline => _isOnline;

  /// Start periodic connectivity checks.
  void start() {
    _check();
    _timer = Timer.periodic(_checkInterval, (_) => _check());
  }

  /// Stop periodic checks and close the stream.
  void dispose() {
    _timer?.cancel();
    _controller.close();
  }

  Future<void> _check() async {
    bool online;
    try {
      final result = await InternetAddress.lookup(_checkHost)
          .timeout(const Duration(seconds: 5));
      online = result.isNotEmpty && result.first.rawAddress.isNotEmpty;
    } catch (_) {
      online = false;
    }

    if (online != _isOnline) {
      _isOnline = online;
      _controller.add(_isOnline);
    }
  }
}
