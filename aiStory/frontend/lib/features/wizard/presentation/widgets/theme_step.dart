import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_providers.dart';

/// A widget that allows the user to select a theme for their story.
class ThemeStep extends ConsumerWidget {
  /// Creates a new [ThemeStep] widget.
  const ThemeStep({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentTheme = ref.watch(wizardProvider).theme;

    // List of available themes with their icons
    final List<Map<String, dynamic>> themes = [
      {'name': 'Adventure', 'icon': Icons.hiking},
      {'name': 'Fantasy', 'icon': Icons.auto_fix_high},
      {'name': 'Space', 'icon': Icons.rocket_launch},
      {'name': 'Mystery', 'icon': Icons.search},
      {'name': 'Fairy Tale', 'icon': Icons.castle},
      {'name': 'Superheroes', 'icon': Icons.shield},
    ];

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Choose a theme for your story',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 24),
          
          // Theme grid
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 1.5,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: themes.length,
              itemBuilder: (context, index) {
                final theme = themes[index];
                final String themeName = theme['name'] as String;
                final IconData themeIcon = theme['icon'] as IconData;
                final bool isSelected = themeName == currentTheme;
                
                return Card(
                  elevation: isSelected ? 8.0 : 1.0,
                  color: isSelected 
                      ? Theme.of(context).colorScheme.primaryContainer 
                      : null,
                  child: InkWell(
                    onTap: () {
                      ref.read(wizardProvider.notifier).updateTheme(themeName);
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            themeIcon,
                            size: 40,
                            color: isSelected 
                                ? Theme.of(context).colorScheme.primary
                                : null,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            themeName,
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: isSelected 
                                  ? FontWeight.bold 
                                  : FontWeight.normal,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          
          const SizedBox(height: 16),
          const Text(
            'The theme will set the tone and setting of your story.',
            style: TextStyle(
              fontStyle: FontStyle.italic,
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }
}