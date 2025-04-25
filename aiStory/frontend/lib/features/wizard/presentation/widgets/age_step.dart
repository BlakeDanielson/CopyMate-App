import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_providers.dart';

/// A widget that allows the user to select the character's age for their story.
class AgeStep extends ConsumerWidget {
  /// Creates a new [AgeStep] widget.
  const AgeStep({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentAge = ref.watch(wizardProvider).age;

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'How old is your character?',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 24),
          
          // Age display
          Center(
            child: Text(
              '$currentAge years old',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 16),
          
          // Age slider
          Slider(
            value: currentAge.toDouble(),
            min: 3,
            max: 18,
            divisions: 15,
            label: currentAge.toString(),
            onChanged: (value) {
              ref.read(wizardProvider.notifier).updateAge(value.toInt());
            },
          ),
          
          const SizedBox(height: 24),
          const Text(
            'Or choose an age group:',
            style: TextStyle(
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 16),
          
          // Age category chips
          Wrap(
            spacing: 8.0,
            children: [
              ChoiceChip(
                label: const Text('Child (5-7)'),
                selected: currentAge >= 5 && currentAge <= 7,
                onSelected: (selected) {
                  if (selected) {
                    ref.read(wizardProvider.notifier).updateAge(6);
                  }
                },
              ),
              ChoiceChip(
                label: const Text('Pre-teen (8-12)'),
                selected: currentAge >= 8 && currentAge <= 12,
                onSelected: (selected) {
                  if (selected) {
                    ref.read(wizardProvider.notifier).updateAge(10);
                  }
                },
              ),
              ChoiceChip(
                label: const Text('Teen'),
                selected: currentAge >= 13 && currentAge <= 17,
                onSelected: (selected) {
                  if (selected) {
                    ref.read(wizardProvider.notifier).updateAge(13);
                  }
                },
              ),
              ChoiceChip(
                label: const Text('Young Adult'),
                selected: currentAge >= 18,
                onSelected: (selected) {
                  if (selected) {
                    ref.read(wizardProvider.notifier).updateAge(18);
                  }
                },
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          const Text(
            'The character\'s age will influence the tone and vocabulary of your story.',
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