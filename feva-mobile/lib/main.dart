import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;

import 'admin/screens/web_dashboard_screen.dart';
import 'auth/bloc/auth_bloc.dart';
import 'auth/models/session_model.dart';
import 'auth/repositories/auth_repository.dart';
import 'auth/screens/login_screen.dart';
import 'boundary/boundary_service.dart';
import 'buildings/screens/building_list_screen.dart';
import 'core/app_config.dart';
import 'core/connectivity_service.dart';
import 'core/widgets/auth_guard.dart';
import 'database/app_database.dart';
import 'dropdown/dropdown_service.dart';
import 'gps/gps_service.dart';
import 'photo/photo_service.dart';
import 'qr/bloc/qr_bloc.dart';
import 'qr/screens/qr_scanner_screen.dart';
import 'spot_check/bloc/spot_check_bloc.dart';
import 'spot_check/screens/spot_check_list_screen.dart';
import 'streets/screens/street_list_screen.dart';
import 'sync/sync_engine.dart';
import 'sync/widgets/offline_status_widget.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const _AppLoader());
}

/// Opens the DB (safe to call after ensureInitialized — only uses
/// path_provider which doesn't need an attached Activity) then renders
/// [FevaApp]. Shows a spinner while loading.
class _AppLoader extends StatefulWidget {
  const _AppLoader();

  @override
  State<_AppLoader> createState() => _AppLoaderState();
}

class _AppLoaderState extends State<_AppLoader> {
  late final Future<AppDatabase> _dbFuture = AppDatabase.open();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<AppDatabase>(
      future: _dbFuture,
      builder: (context, snap) {
        if (snap.hasError) {
          return MaterialApp(
            home: Scaffold(
              body: Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text(
                    'Failed to open database:\n${snap.error}',
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
            ),
          );
        }
        if (!snap.hasData) {
          return const MaterialApp(
            home: Scaffold(
              body: Center(child: CircularProgressIndicator()),
            ),
          );
        }
        return FevaApp(db: snap.data!);
      },
    );
  }
}

class FevaApp extends StatefulWidget {
  final AppDatabase db;

  const FevaApp({super.key, required this.db});

  @override
  State<FevaApp> createState() => _FevaAppState();
}

class _FevaAppState extends State<FevaApp> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      SyncEngine.registerBackgroundTask().catchError(
        (Object e) => debugPrint('Background task registration failed: $e'),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider<AppDatabase>.value(value: widget.db),
        RepositoryProvider<AuthRepository>(
          create: (_) => AuthRepository(),
        ),
        RepositoryProvider<GpsService>(
          create: (_) => GpsService(),
        ),
        RepositoryProvider<BoundaryService>(
          create: (ctx) => BoundaryService(db: ctx.read<AppDatabase>()),
        ),
        RepositoryProvider<SyncEngine>(
          create: (ctx) => SyncEngine(db: ctx.read<AppDatabase>()),
        ),
        RepositoryProvider<DropdownService>(
          create: (ctx) => DropdownService(db: ctx.read<AppDatabase>()),
        ),
        RepositoryProvider<ConnectivityService>(
          create: (_) => ConnectivityService()..start(),
        ),
        RepositoryProvider<PhotoService>(
          create: (ctx) => PhotoService(
            db: ctx.read<AppDatabase>(),
            userId: 'current_user', // updated at capture time via session
          ),
        ),
      ],
      child: BlocProvider<AuthBloc>(
        create: (ctx) => AuthBloc(
          authRepository: ctx.read<AuthRepository>(),
          db: ctx.read<AppDatabase>(),
        )..add(const AuthSessionChecked()),
        child: MaterialApp(
          title: 'FEVA',
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
            useMaterial3: true,
          ),
          home: const AuthGuard(
            loginScreen: LoginScreen(),
            child: _HomeRedirect(),
          ),
        ),
      ),
    );
  }
}

class _HomeRedirect extends StatelessWidget {
  const _HomeRedirect();

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        if (state is AuthAuthenticated) {
          final role = state.session.role.toLowerCase();
          
          return Scaffold(
            appBar: AppBar(
              title: const Text('FEVA'),
              actions: [
                IconButton(
                  icon: const Icon(Icons.logout),
                  onPressed: () {
                    context.read<AuthBloc>().add(const AuthLogoutRequested());
                  },
                ),
              ],
            ),
            body: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      _getRoleIcon(role),
                      size: 64,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Welcome, ${state.session.username}!',
                      style: Theme.of(context).textTheme.headlineSmall,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Chip(
                      label: Text(
                        role.toUpperCase(),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      backgroundColor: _getRoleColor(role),
                    ),
                    if (state.session.lgaCode != null) ...[
                      const SizedBox(height: 4),
                      Chip(
                        avatar: const Icon(Icons.location_on, size: 16),
                        label: Text(
                          'LGA: ${state.session.lgaCode}',
                          style: const TextStyle(fontSize: 13),
                        ),
                        backgroundColor: Colors.green.shade50,
                      ),
                    ],
                    const SizedBox(height: 16),
                    OfflineStatusWidget(
                      syncEngine: context.read<SyncEngine>(),
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: () =>
                            context.read<SyncEngine>().triggerManualSync(),
                        icon: const Icon(Icons.sync),
                        label: const Text('Sync Now'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.all(14),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    ..._buildRoleSpecificButtons(context, state.session, role),
                  ],
                ),
              ),
            ),
          );
        }
        return const LoginScreen();
      },
    );
  }

  IconData _getRoleIcon(String role) {
    switch (role) {
      case 'admin':
        return Icons.admin_panel_settings;
      case 'supervisor':
        return Icons.supervisor_account;
      case 'enumerator':
      default:
        return Icons.person;
    }
  }

  Color _getRoleColor(String role) {
    switch (role) {
      case 'admin':
        return Colors.red.shade100;
      case 'supervisor':
        return Colors.blue.shade100;
      case 'enumerator':
      default:
        return Colors.green.shade100;
    }
  }

  List<Widget> _buildRoleSpecificButtons(
      BuildContext context, SessionModel session, String role) {
    final buttons = <Widget>[];

    // All roles can access data capture
    buttons.addAll([
      SizedBox(
        width: double.infinity,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => StreetListScreen(session: session),
              ),
            );
          },
          icon: const Icon(Icons.map),
          label: const Text('Streets'),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.all(16),
          ),
        ),
      ),
      const SizedBox(height: 12),
      SizedBox(
        width: double.infinity,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => BuildingListScreen(session: session),
              ),
            );
          },
          icon: const Icon(Icons.business),
          label: const Text('Buildings'),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.all(16),
          ),
        ),
      ),
    ]);

    // Supervisor and Admin can access spot-check and QR scan
    if (role == 'supervisor' || role == 'admin') {
      buttons.addAll([
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              final spotCheckBloc = SpotCheckBloc(
                db: context.read<AppDatabase>(),
                httpClient: http.Client(),
                baseUrl: AppConfig.backendBaseUrl,
                accessToken: session.accessToken,
                assignedLga: session.lgaCode ?? '',
                supervisorId: session.userId,
              )..add(const LoadSpotCheckRecords());

              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => BlocProvider.value(
                    value: spotCheckBloc,
                    child: const SpotCheckListScreen(),
                  ),
                ),
              );
            },
            icon: const Icon(Icons.fact_check),
            label: const Text('Spot Check'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(16),
              backgroundColor: Colors.blue.shade700,
              foregroundColor: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => BlocProvider<QrBloc>(
                    create: (ctx) => QrBloc(
                      db: ctx.read<AppDatabase>(),
                      httpClient: http.Client(),
                      baseUrl: AppConfig.backendBaseUrl,
                      accessToken: session.accessToken,
                      supervisorId: session.userId,
                    ),
                    child: const QrScannerScreen(),
                  ),
                ),
              );
            },
            icon: const Icon(Icons.qr_code_scanner),
            label: const Text('Scan QR Code'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(16),
              backgroundColor: Colors.teal.shade700,
              foregroundColor: Colors.white,
            ),
          ),
        ),
      ]);
    }

    // Admin-only features
    if (role == 'admin') {
      buttons.addAll([
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const WebDashboardScreen(
                    url: '${AppConfig.backendBaseUrl}/qa/',
                    title: 'QA Dashboard',
                  ),
                ),
              );
            },
            icon: const Icon(Icons.bar_chart),
            label: const Text('QA Dashboard'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(16),
              backgroundColor: Colors.blue.shade900,
              foregroundColor: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const WebDashboardScreen(
                    url: '${AppConfig.backendBaseUrl}/dashboard/',
                    title: 'Admin Dashboard',
                  ),
                ),
              );
            },
            icon: const Icon(Icons.dashboard),
            label: const Text('Admin Dashboard'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(16),
              backgroundColor: Colors.red.shade700,
              foregroundColor: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const WebDashboardScreen(
                    url: '${AppConfig.backendBaseUrl}/api/v1/admin/users',
                    title: 'User Management',
                  ),
                ),
              );
            },
            icon: const Icon(Icons.people),
            label: const Text('User Management'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(16),
              backgroundColor: Colors.red.shade700,
              foregroundColor: Colors.white,
            ),
          ),
        ),
      ]);
    }

    return buttons;
  }
}
