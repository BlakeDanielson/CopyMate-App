import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ai_story/features/auth/domain/models/auth_state.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_providers.dart';
import 'package:ai_story/features/auth/presentation/widgets/test_mode_banner.dart';

/// Home screen of the application
class HomeScreen extends ConsumerWidget {
  /// Creates a new [HomeScreen]
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);
    final isTestMode = authState.isTestMode;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Story Creator'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: isTestMode ? 'Exit Test Mode' : 'Logout',
            onPressed: () {
              if (isTestMode) {
                ref.read(authNotifierProvider.notifier).exitTestMode();
              } else {
                ref.read(authNotifierProvider.notifier).logout();
              }
              context.go('/login');
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Show test mode banner if in test mode
          if (isTestMode) const TestModeBanner(),
          
          // Main content
          Expanded(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.auto_stories,
                      size: 100,
                      color: Colors.purple,
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Welcome to AI Story Creator',
                      style: Theme.of(context).textTheme.headlineMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Create amazing stories with the help of AI',
                      style: Theme.of(context).textTheme.bodyLarge,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),
                    ElevatedButton.icon(
                      onPressed: () {
                        // Navigate to create story screen
                        Navigator.of(context).pushNamed('/create-story');
                      },
                      icon: const Icon(Icons.add),
                      label: const Text('Create New Story'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}