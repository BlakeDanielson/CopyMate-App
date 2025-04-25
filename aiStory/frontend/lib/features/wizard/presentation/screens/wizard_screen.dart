import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_providers.dart';
import 'package:ai_story/features/wizard/presentation/widgets/name_step.dart';
import 'package:ai_story/features/wizard/presentation/widgets/age_step.dart';
import 'package:ai_story/features/wizard/presentation/widgets/theme_step.dart';

/// The main screen for the story creation wizard.
///
/// This widget orchestrates the step-by-step process of creating a story,
/// displaying the appropriate content for each step and handling navigation
/// between steps.
class WizardScreen extends ConsumerWidget {
  /// Creates a new [WizardScreen] widget.
  const WizardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentStep = ref.watch(wizardCurrentStepProvider);
    final canGoNext = ref.watch(canGoNextProvider);
    final canGoPrevious = ref.watch(canGoPreviousProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create Your Story'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: Stepper(
              currentStep: currentStep,
              controlsBuilder: (context, details) {
                // Remove default stepper controls as we'll use our own
                return Container();
              },
              onStepTapped: (step) {
                // Allow jumping to previous steps but not ahead
                if (step <= currentStep) {
                  ref.read(wizardProvider.notifier).goToStep(step);
                }
              },
              steps: _buildSteps(context),
            ),
          ),
          _buildNavigationButtons(context, ref, canGoNext, canGoPrevious),
        ],
      ),
    );
  }

  /// Builds the list of steps for the stepper.
  List<Step> _buildSteps(BuildContext context) {
    return [
      Step(
        title: const Text('Character Name'),
        content: Container(
          alignment: Alignment.centerLeft,
          child: const NameStep(),
        ),
        isActive: true,
      ),
      Step(
        title: const Text('Character Age'),
        content: Container(
          alignment: Alignment.centerLeft,
          child: const AgeStep(),
        ),
        isActive: true,
      ),
      Step(
        title: const Text('Story Theme'),
        content: Container(
          alignment: Alignment.centerLeft,
          child: const ThemeStep(),
        ),
        isActive: true,
      ),
    ];
  }

  /// Builds the navigation buttons (Next/Back) for the wizard.
  Widget _buildNavigationButtons(
    BuildContext context,
    WidgetRef ref,
    bool canGoNext,
    bool canGoPrevious,
  ) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          ElevatedButton(
            onPressed: canGoPrevious
                ? () => ref.read(wizardProvider.notifier).previousStep()
                : null,
            child: const Text('Back'),
          ),
          ElevatedButton(
            onPressed: canGoNext
                ? () => ref.read(wizardProvider.notifier).nextStep()
                : null,
            child: const Text('Next'),
          ),
        ],
      ),
    );
  }
}