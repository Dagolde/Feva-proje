import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;

import '../../auth/bloc/auth_bloc.dart';
import '../../auth/models/session_model.dart';
import '../../boundary/boundary_service.dart';
import '../../core/app_config.dart';
import '../../database/app_database.dart';
import '../../qr/bloc/qr_bloc.dart';
import '../../qr/screens/qr_scanner_screen.dart';
import '../bloc/street_bloc.dart';
import 'street_form_screen.dart';
import 'street_map_screen.dart';

/// Displays all streets captured by the current enumerator.
///
/// Requirements: 2.1, 2.6, 2.7
class StreetListScreen extends StatelessWidget {
  final SessionModel session;

  const StreetListScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => StreetBloc(
        db: context.read<AppDatabase>(),
        boundaryService: context.read<BoundaryService>(),
      )..add(const LoadStreets()),
      child: _StreetListView(session: session),
    );
  }
}

class _StreetListView extends StatelessWidget {
  final SessionModel session;
  const _StreetListView({required this.session});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Streets'),
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
                builder: (_) => StreetMapScreen(session: session),
              ),
            ),
          ),
        ],
      ),
      body: BlocBuilder<StreetBloc, StreetState>(
        builder: (context, state) {
          if (state is StreetLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state is StreetError) {
            return Center(child: Text('Error: ${state.message}'));
          }
          if (state is StreetListLoaded) {
            if (state.streets.isEmpty) {
              return const Center(
                child: Text('No streets captured yet.\nTap + to add one.',
                    textAlign: TextAlign.center),
              );
            }
            return ListView.separated(
              itemCount: state.streets.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final street = state.streets[index];
                return ListTile(
                  leading: const Icon(Icons.add_road),
                  title: Text(street.streetName),
                  subtitle: Text(
                      '${street.streetId} · ${street.streetType} · ${street.syncStatus}'),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.copy, size: 18),
                        tooltip: 'Copy Street ID',
                        onPressed: () {
                          Clipboard.setData(
                              ClipboardData(text: street.streetId));
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                  'Copied: ${street.streetId}'),
                              duration: const Duration(seconds: 2),
                            ),
                          );
                        },
                      ),
                      _SyncStatusIcon(status: street.syncStatus),
                    ],
                  ),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => BlocProvider.value(
                        value: context.read<StreetBloc>(),
                        child: StreetFormScreen(
                          session: session,
                          existingStreet: street,
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
              value: context.read<StreetBloc>(),
              child: StreetFormScreen(session: session),
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
