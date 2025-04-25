import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/features/wizard/domain/models/wizard_state.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_state_notifier.dart';

/// Provider for the wizard state notifier.
///
/// This provider exposes the [WizardStateNotifier] which manages the state of the
/// wizard throughout the story creation process.
final wizardProvider = StateNotifierProvider<WizardStateNotifier, WizardState>((ref) {
  return WizardStateNotifier();
});

/// Provider for the current step in the wizard.
///
/// This provider selects just the current step from the wizard state for
/// widgets that only need to know which step is active.
final wizardCurrentStepProvider = Provider<int>((ref) {
  final wizardState = ref.watch(wizardProvider);
  return wizardState.currentStep;
});

/// Provider to determine if the Next button should be enabled.
///
/// This provider computes whether the user can proceed to the next step based on
/// the current state of the wizard.
final canGoNextProvider = Provider<bool>((ref) {
  final wizardNotifier = ref.read(wizardProvider.notifier);
  return wizardNotifier.canGoNext();
});

/// Provider to determine if the Back button should be enabled.
///
/// This provider computes whether the user can go back to the previous step based on
/// the current state of the wizard.
final canGoPreviousProvider = Provider<bool>((ref) {
  final wizardNotifier = ref.read(wizardProvider.notifier);
  return wizardNotifier.canGoPrevious();
});