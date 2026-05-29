import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../bloc/qr_bloc.dart';
import 'qr_detail_screen.dart';

/// QR code scanner screen — decodes QR → building_id and loads the record.
///
/// Requirements: 17.1, 17.2, 17.7
class QrScannerScreen extends StatefulWidget {
  const QrScannerScreen({super.key});

  @override
  State<QrScannerScreen> createState() => _QrScannerScreenState();
}

class _QrScannerScreenState extends State<QrScannerScreen> {
  bool _scanned = false;

  @override
  Widget build(BuildContext context) {
    return BlocListener<QrBloc, QrState>(
      listener: (context, state) {
        if (state is QrBuildingFound ||
            state is QrBuildingFoundRemote ||
            state is QrStreetFound ||
            state is QrStreetFoundRemote) {
          Navigator.of(context).push(MaterialPageRoute(
            builder: (_) => BlocProvider.value(
              value: context.read<QrBloc>(),
              child: const QrDetailScreen(),
            ),
          )).then((_) => setState(() => _scanned = false));
        } else if (state is QrNotFound) {
          setState(() => _scanned = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(state.message), backgroundColor: Colors.red),
          );
        } else if (state is QrError) {
          setState(() => _scanned = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(state.message), backgroundColor: Colors.red),
          );
        }
      },
      child: Scaffold(
        appBar: AppBar(title: const Text('Scan QR Code')),
        body: Stack(
          children: [
            MobileScanner(
              onDetect: (capture) {
                if (_scanned) return;
                final barcode = capture.barcodes.firstOrNull;
                final value = barcode?.rawValue;
                if (value != null && value.isNotEmpty) {
                  setState(() => _scanned = true);
                  context.read<QrBloc>().add(ScanQrCode(value));
                }
              },
            ),
            BlocBuilder<QrBloc, QrState>(
              builder: (context, state) {
                if (state is QrLoading) {
                  return const Center(child: CircularProgressIndicator());
                }
                return const SizedBox.shrink();
              },
            ),
            Positioned(
              bottom: 32,
              left: 0,
              right: 0,
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.black54,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'Point camera at building or street QR code',
                    style: TextStyle(color: Colors.white),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
