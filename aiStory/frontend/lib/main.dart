import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ai_story/config/env_config.dart';
import 'package:ai_story/config/router.dart';
import 'package:ai_story/core/theme/app_theme.dart';
import 'package:ai_story/core/utils/logger.dart';

/// The entry point for the application
void main() async {
  // Ensure Flutter is initialized
  WidgetsFlutterBinding.ensureInitialized();

  try {
    // Initialize environment configuration
    await EnvConfig.initialize('development');
    
    // Log application start
    logger.i('Starting AI Story Creator application');
    
    // Run the app
    runApp(
      const ProviderScope(
        child: MyApp(),
      ),
    );
  } catch (e, stackTrace) {
    logger.e('Error during app initialization', e, stackTrace);
    rethrow;
  }
}

/// The root widget of the application
class MyApp extends ConsumerWidget {
  /// Creates a new instance of [MyApp]
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final GoRouter appRouter = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'AI Story Creator',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      routerConfig: appRouter,
    );
  }
}
