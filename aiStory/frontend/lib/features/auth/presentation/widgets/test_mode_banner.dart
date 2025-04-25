import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_providers.dart';

/// A banner widget that appears when the app is running in test mode
class TestModeBanner extends ConsumerWidget {
  /// Creates a new [TestModeBanner]
  const TestModeBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      color: Colors.amber.shade100,
      child: Row(
        children: [
          const Icon(
            Icons.info_outline,
            color: Colors.amber,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Test Mode Active',
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.amber.shade900,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              ref.read(authNotifierProvider.notifier).exitTestMode();
            },
            style: TextButton.styleFrom(
              backgroundColor: Colors.amber.shade200,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              minimumSize: const Size(0, 0),
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            child: Text(
              'Exit Test Mode',
              style: theme.textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.amber.shade900,
              ),
            ),
          ),
        ],
      ),
    );
  }
}