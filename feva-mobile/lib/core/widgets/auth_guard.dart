import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../auth/bloc/auth_bloc.dart';

/// Wraps [child] and ensures the user is authenticated before showing it.
///
/// If the session is expired or absent, dispatches [AuthSessionChecked] and
/// shows [loginScreen] instead.
class AuthGuard extends StatelessWidget {
  final Widget child;
  final Widget loginScreen;

  const AuthGuard({
    super.key,
    required this.child,
    required this.loginScreen,
  });

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        if (state is AuthAuthenticated && !state.session.isExpired) {
          return child;
        }

        // Show a loading spinner only while the session check is in flight.
        if (state is AuthLoading) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        return loginScreen;
      },
    );
  }
}
