import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;

import '../../auth/bloc/auth_bloc.dart';
import '../../auth/models/session_model.dart';
import '../../boundary/boundary_service.dart';
import '../../core/app_config.dart';
import '../../database/app_database.dart';
import '../../qr/bloc/qr_bloc.dart';
import '../../qr/screens/qr_scanner_screen.dart';
import '../bloc/building_bloc.dart';
import 'building_form_screen.dart';
import 'building_map_screen.dart';

/// Displays all buildings captured by the current enumerator.
///
/// Requirements: 3.1, 3.7, 3.8
class BuildingListScreen extends StatelessWidget {
  final SessionModel session;

  const BuildingListScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => BuildingBloc(
        db: context.read<AppDatabase>(),
        boundaryService: context.read<BoundaryService>(),
      )..add(const LoadBuildings()),
      child: _BuildingListView(session: session),
    );
  }
}

class _BuildingListView extends StatelessWidget {
  final SessionModel session;
  const _BuildingListView({required this.session});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Buildings'),
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            tooltip: 'Scan QR',
            onPressed: () {
              final authState = context.read<AuthBloc>().state;
              final session = authState is AuthAuthenticated ? authState.session : null;
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => BlocProvider<QrBloc>(
                    create: (ctx) => QrBloc(
                      db: ctx.read<AppDatabase>(),
                      httpClient: http.Client(),
                      baseUrl: AppConfig.backendBaseUrl,
                      accessToken: session?.accessToken ?? '',
                      supervisorId: session?.userId ?? '',
                    ),
                    child: const QrScannerScreen(),
                  ),
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.map),
            tooltip: 'Map view',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => BuildingMapScreen(session: session),
              ),
            ),
          ),
        ],
      ),
      body: BlocBuilder<BuildingBloc, BuildingState>(
        builder: (context, state) {
          if (state is BuildingLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state is BuildingError) {
            return Center(child: Text('Error: ${state.message}'));
          }
          if (state is BuildingListLoaded) {
            if (state.buildings.isEmpty) {
              return const Center(
                child: Text('No buildings captured yet.\nTap + to add one.',
                    textAlign: TextAlign.center),
              );
            }
            return ListView.separated(
              itemCount: state.buildings.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final b = state.buildings[index];
                return ListTile(
                  leading: const Icon(Icons.apartment),
                  title: Text(b.buildingId),
                  subtitle: Text(
                      '${b.buildingType} · ${b.numberOfFloors}F · ${b.syncStatus}'),
                  trailing: _SyncStatusIcon(status: b.syncStatus),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => BlocProvider.value(
                        value: context.read<BuildingBloc>(),
                        child: BuildingFormScreen(
                          session: session,
                          existingBuilding: b,
                        ),
                      ),
                    ),
                  ),
                );
              },
            );
          }
          return const SizedBox.shrink();
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => BlocProvider.value(
              value: context.read<BuildingBloc>(),
              child: BuildingFormScreen(session: session),
            ),
          ),
        ),
        child: const Icon(Icons.add),
      ),
    );
  }
}

class _SyncStatusIcon extends StatelessWidget {
  final String status;
  const _SyncStatusIcon({required this.status});

  @override
  Widget build(BuildContext context) {
    switch (status) {
      case 'synced':
        return const Icon(Icons.cloud_done, color: Colors.green);
      case 'failed':
        return const Icon(Icons.cloud_off, color: Colors.red);
      default:
        return const Icon(Icons.cloud_upload_outlined, color: Colors.orange);
    }
  }
}
