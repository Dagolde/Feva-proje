import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../auth/models/session_model.dart';
import '../../database/app_database.dart';
import '../../map/map_widget.dart';
import '../bloc/building_bloc.dart';

/// Map view showing all captured building points.
///
/// Requirements: 3.3, 8.4, 8.6
class BuildingMapScreen extends StatelessWidget {
  final SessionModel session;

  const BuildingMapScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => BuildingBloc(
        db: context.read<AppDatabase>(),
        boundaryService: context.read(),
      )..add(const LoadBuildings()),
      child: Scaffold(
        appBar: AppBar(title: const Text('Building Map')),
        body: BlocBuilder<BuildingBloc, BuildingState>(
          builder: (context, state) {
            if (state is BuildingLoading) {
              return const Center(child: CircularProgressIndicator());
            }
            return const MapLibreMapWidget();
          },
        ),
      ),
    );
  }
}
