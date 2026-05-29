import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../bloc/auth_bloc.dart';

class TwoFactorScreen extends StatefulWidget {
  final String username;
  final String password;

  const TwoFactorScreen({
    super.key,
    required this.username,
    required this.password,
  });

  @override
  State<TwoFactorScreen> createState() => _TwoFactorScreenState();
}

class _TwoFactorScreenState extends State<TwoFactorScreen> {
  final _codeController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  void _verify(BuildContext context) {
    if (!_formKey.currentState!.validate()) return;
    context.read<AuthBloc>().add(AuthLoginRequested(
          username: widget.username,
          password: widget.password,
          totpCode: _codeController.text.trim(),
        ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Two-Factor Authentication')),
      body: BlocConsumer<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthAuthenticated) {
            // Pop back to root; AppRouter/AuthGuard will handle navigation.
            Navigator.of(context).popUntil((route) => route.isFirst);
          } else if (state is AuthError && state.code != 'totp_required') {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: Colors.red.shade700,
              ),
            );
          } else if (state is AuthLocked) {
            Navigator.of(context).pop();
          }
        },
        builder: (context, state) {
          final isLoading = state is AuthLoading;

          return SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.security, size: 64),
                    const SizedBox(height: 16),
                    Text(
                      'Enter your 6-digit authentication code',
                      style: Theme.of(context).textTheme.titleMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),
                    Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          TextFormField(
                            controller: _codeController,
                            decoration: const InputDecoration(
                              labelText: 'Authentication Code',
                              prefixIcon: Icon(Icons.pin_outlined),
                              border: OutlineInputBorder(),
                              counterText: '',
                            ),
                            keyboardType: TextInputType.number,
                            inputFormatters: [
                              FilteringTextInputFormatter.digitsOnly,
                            ],
                            maxLength: 6,
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                                fontSize: 24, letterSpacing: 8),
                            textInputAction: TextInputAction.done,
                            onFieldSubmitted: (_) => _verify(context),
                            validator: (v) {
                              if (v == null || v.trim().isEmpty) {
                                return 'Code is required';
                              }
                              if (v.trim().length != 6) {
                                return 'Code must be 6 digits';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 24),
                          SizedBox(
                            width: double.infinity,
                            height: 48,
                            child: ElevatedButton(
                              onPressed:
                                  isLoading ? null : () => _verify(context),
                              child: isLoading
                                  ? const SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                          strokeWidth: 2),
                                    )
                                  : const Text('Verify'),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
