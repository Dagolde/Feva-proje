import 'package:flutter/material.dart';

/// Displays a warning banner when one or more photo records have broken file
/// references (i.e. `broken_ref_flag = 1`).
///
/// Returns [SizedBox.shrink] when [brokenCount] is zero so callers can embed
/// this widget unconditionally in the submission list without visual noise.
class BrokenRefWarning extends StatelessWidget {
  /// Number of photos with broken references.
  final int brokenCount;

  const BrokenRefWarning({super.key, required this.brokenCount});

  @override
  Widget build(BuildContext context) {
    if (brokenCount == 0) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.amber.shade100,
        border: Border.all(color: Colors.amber.shade700),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber_rounded,
              color: Colors.amber.shade800, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '⚠ $brokenCount photo(s) have missing files and will not sync',
              style: TextStyle(
                color: Colors.amber.shade900,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
