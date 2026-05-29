import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../auth/models/session_model.dart';
import '../../database/app_database.dart';
import '../../map/map_widget.dart';
import '../bloc/street_bloc.dart';

/// Map view showing all captured street points.
///
/// Requirements: 2.3, 8.4, 8.6
class StreetMapScreen extends StatelessWidget {
  final SessionModel session;

  const StreetMapScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => StreetBloc(
        db: context.read<AppDatabase>(),
        boundaryService: context.read(),
      )..add(const LoadStreets()),
      child: Scaffold(
        appBar: AppBar(title: const Text('Street Map')),
        body: BlocBuilder<StreetBloc, StreetState>(
          builder: (context, state) {
            if (state is StreetLoading) {
              return const Center(child: CircularProgressIndicator());
            }
            // The MapLibreMapWidget already renders captured points from the
            // local DB; this screen simply wraps it with the street context.
            return const MapLibreMapWidget();
          },
        ),
      ),
    );
  }
}
