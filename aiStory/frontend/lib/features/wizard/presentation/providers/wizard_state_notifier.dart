import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/features/wizard/domain/models/wizard_state.dart';

/// A state notifier responsible for managing the wizard's state throughout
/// the story creation process.
class WizardStateNotifier extends StateNotifier<WizardState> {
  /// Creates a new [WizardStateNotifier] with an initial state.
  WizardStateNotifier() : super(const WizardState());

  /// The total number of steps in the wizard process.
  static const totalSteps = 3;

  /// Moves to the next step if possible.
  void nextStep() {
    if (canGoNext()) {
      state = state.copyWith(
        currentStep: state.currentStep + 1,
      );
    }
  }

  /// Moves to the previous step if possible.
  void previousStep() {
    if (canGoPrevious()) {
      state = state.copyWith(
        currentStep: state.currentStep - 1,
      );
    }
  }

  /// Checks if it's possible to move to the next step.
  bool canGoNext() {
    return state.currentStep < totalSteps - 1 && state.isCurrentStepValid;
  }

  /// Checks if it's possible to move to the previous step.
  bool canGoPrevious() {
    return state.currentStep > 0;
  }

  /// Updates the current step's validation status.
  void updateStepValidity(bool isValid) {
    state = state.copyWith(isCurrentStepValid: isValid);
  }

  /// Sets the wizard to a specific step index.
  void goToStep(int step) {
    if (step >= 0 && step < totalSteps) {
      state = state.copyWith(currentStep: step);
    }
  }
  
  /// Updates the character name in the wizard state.
  void updateName(String name) {
    state = state.copyWith(
      name: name,
      isCurrentStepValid: name.trim().isNotEmpty,
    );
  }
  
  /// Updates the character age in the wizard state.
  void updateAge(int age) {
    state = state.copyWith(
      age: age,
      isCurrentStepValid: age > 0 && age <= 120,
    );
  }
  
  /// Updates the story theme in the wizard state.
  void updateTheme(String theme) {
    state = state.copyWith(
      theme: theme,
      isCurrentStepValid: theme.trim().isNotEmpty,
    );
  }
}