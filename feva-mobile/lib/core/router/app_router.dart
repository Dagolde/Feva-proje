import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;

import '../../admin/screens/web_dashboard_screen.dart';
import '../../auth/bloc/auth_bloc.dart';
import '../../auth/screens/login_screen.dart';
import '../../auth/screens/two_factor_screen.dart';
import '../../database/app_database.dart';
import '../../qr/bloc/qr_bloc.dart';
import '../../qr/screens/qr_scanner_screen.dart';
import '../../spot_check/bloc/spot_check_bloc.dart';
import '../../spot_check/screens/spot_check_list_screen.dart';
import '../widgets/auth_guard.dart';
import '../app_config.dart';

// ── Route name constants ──────────────────────────────────────────────────────

class Routes {
  static const home = '/';
  static const login = '/login';
  static const twoFactor = '/two-factor';
  static const streets = '/streets';
  static const streetsNew = '/streets/new';
  static const buildings = '/buildings';
  static const buildingsNew = '/buildings/new';
  static const history = '/history';
  static const spotCheck = '/spot-check';
  static const qaDashboard = '/qa-dashboard';
  static const qrScan = '/qr-scan';
  static const admin = '/admin';
}

// ── RBAC permission matrix ────────────────────────────────────────────────────

const _enumeratorRoutes = {
  Routes.streets,
  Routes.streetsNew,
  Routes.buildings,
  Routes.buildingsNew,
  Routes.history,
};

const _supervisorRoutes = {
  Routes.streets,
  Routes.streetsNew,
  Routes.buildings,
  Routes.buildingsNew,
  Routes.history,
  Routes.spotCheck,
  Routes.qrScan,
};

// Admin has access to all routes — checked by exclusion.

bool _isRoutePermitted(String role, String routeName) {
  switch (role) {
    case 'enumerator':
      return _enumeratorRoutes.contains(routeName);
    case 'supervisor':
      return _supervisorRoutes.contains(routeName);
    case 'admin':
      return true;
    default:
      return false;
  }
}

// ── Placeholder screens ───────────────────────────────────────────────────────

class _PlaceholderScreen extends StatelessWidget {
  final String title;
  const _PlaceholderScreen({required this.title});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Center(child: Text(title)),
    );
  }
}

class UnauthorizedScreen extends StatelessWidget {
  const UnauthorizedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Access Denied')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.block, size: 64, color: Colors.red),
            SizedBox(height: 16),
            Text(
              'You do not have permission to access this page.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

// ── AppRouter ─────────────────────────────────────────────────────────────────

class AppRouter {
  /// Generates a [Route] for the given [RouteSettings].
  ///
  /// Public routes (login, two-factor) are always accessible.
  /// All other routes are gated by [AuthGuard] and the RBAC matrix.
  static Route<dynamic> generateRoute(
    RouteSettings settings,
    BuildContext context,
  ) {
    final name = settings.name ?? Routes.home;

    // Public routes — no auth required.
    if (name == Routes.login) {
      return MaterialPageRoute(
        settings: settings,
        builder: (_) => const LoginScreen(),
      );
    }

    if (name == Routes.twoFactor) {
      final args = settings.arguments as Map<String, String>?;
      return MaterialPageRoute(
        settings: settings,
        builder: (_) => TwoFactorScreen(
          username: args?['username'] ?? '',
          password: args?['password'] ?? '',
        ),
      );
    }

    // Home route — wrapped in AuthGuard.
    if (name == Routes.home) {
      return MaterialPageRoute(
        settings: settings,
        builder: (_) => AuthGuard(
          loginScreen: const LoginScreen(),
          child: _roleHome(context),
        ),
      );
    }

    // All other routes require authentication + RBAC check.
    return MaterialPageRoute(
      settings: settings,
      builder: (_) {
        final authState = context.read<AuthBloc>().state;
        if (authState is! AuthAuthenticated || authState.session.isExpired) {
          return const LoginScreen();
        }

        final role = authState.session.role;
        if (!_isRoutePermitted(role, name)) {
          return const UnauthorizedScreen();
        }

        return _buildScreen(name, settings.arguments, context);
      },
    );
  }

  /// Returns the role-appropriate home screen widget.
  static Widget _roleHome(BuildContext context) {
    final authState = context.read<AuthBloc>().state;
    if (authState is! AuthAuthenticated) return const LoginScreen();

    switch (authState.session.role) {
      case 'admin':
        return const _PlaceholderScreen(title: 'Admin Dashboard');
      case 'supervisor':
        return const _PlaceholderScreen(title: 'Supervisor Dashboard');
      default:
        return const _PlaceholderScreen(title: 'Streets');
    }
  }

  static Widget _buildScreen(String name, Object? arguments, BuildContext context) {
    switch (name) {
      case Routes.streets:
        return const _PlaceholderScreen(title: 'Streets');
      case Routes.streetsNew:
        return const _PlaceholderScreen(title: 'New Street');
      case Routes.buildings:
        return const _PlaceholderScreen(title: 'Buildings');
      case Routes.buildingsNew:
        return const _PlaceholderScreen(title: 'New Building');
      case Routes.history:
        return const _PlaceholderScreen(title: 'My History');
      case Routes.spotCheck:
        final authState = context.read<AuthBloc>().state;
        final session = authState is AuthAuthenticated ? authState.session : null;
        return BlocProvider<SpotCheckBloc>(
          create: (ctx) => SpotCheckBloc(
            db: ctx.read<AppDatabase>(),
            httpClient: http.Client(),
            baseUrl: AppConfig.backendBaseUrl,
            accessToken: session?.accessToken ?? '',
            assignedLga: session?.lgaCode ?? '',
            supervisorId: session?.userId ?? '',
          )..add(const LoadSpotCheckRecords()),
          child: const SpotCheckListScreen(),
        );
      case Routes.qaDashboard:
        return const WebDashboardScreen(
          url: '${AppConfig.backendBaseUrl}/qa/',
          title: 'QA Dashboard',
        );
      case Routes.qrScan:
        final authState = context.read<AuthBloc>().state;
        final session = authState is AuthAuthenticated ? authState.session : null;
        return BlocProvider<QrBloc>(
          create: (ctx) => QrBloc(
            db: ctx.read<AppDatabase>(),
            httpClient: http.Client(),
            baseUrl: AppConfig.backendBaseUrl,
            accessToken: session?.accessToken ?? '',
            supervisorId: session?.userId ?? '',
          ),
          child: const QrScannerScreen(),
        );
      case Routes.admin:
        return const _PlaceholderScreen(title: 'Admin');
      default:
        return const _PlaceholderScreen(title: 'Not Found');
    }
  }
}
