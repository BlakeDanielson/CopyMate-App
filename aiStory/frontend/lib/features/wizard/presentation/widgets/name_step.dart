import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_providers.dart';

/// A widget that allows the user to enter a character name for their story.
class NameStep extends ConsumerWidget {
  /// Creates a new [NameStep] widget.
  const NameStep({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentName = ref.watch(wizardProvider).name;

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'What should we call your character?',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            decoration: const InputDecoration(
              labelText: 'Character Name',
              hintText: 'Enter a name for your story character',
              border: OutlineInputBorder(),
            ),
            controller: TextEditingController(text: currentName),
            onChanged: (value) => ref.read(wizardProvider.notifier).updateName(value),
            textCapitalization: TextCapitalization.words,
            maxLength: 50,
          ),
          const SizedBox(height: 16),
          const Text(
            'This name will be used throughout your story.',
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