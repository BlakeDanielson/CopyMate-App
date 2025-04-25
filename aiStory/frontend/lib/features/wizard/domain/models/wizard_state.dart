/// Represents the state of the story creation wizard process.
class WizardState {
  /// The current step index in the wizard (0-based).
  final int currentStep;
  
  /// Whether the current step has valid data to proceed.
  final bool isCurrentStepValid;
  
  /// The character name entered in the Name step.
  final String name;
  
  /// The character age selected in the Age step.
  final int age;
  
  /// The theme selected in the Theme step.
  final String theme;
  
  /// Creates a new [WizardState] instance.
  const WizardState({
    this.currentStep = 0,
    this.isCurrentStepValid = true,
    this.name = '',
    this.age = 8,
    this.theme = '',
  });
  
  /// Creates a copy of this state with the specified fields updated.
  WizardState copyWith({
    int? currentStep,
    bool? isCurrentStepValid,
    String? name,
    int? age,
    String? theme,
  }) {
    return WizardState(
      currentStep: currentStep ?? this.currentStep,
      isCurrentStepValid: isCurrentStepValid ?? this.isCurrentStepValid,
      name: name ?? this.name,
      age: age ?? this.age,
      theme: theme ?? this.theme,
    );
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is WizardState && 
           other.currentStep == currentStep && 
           other.isCurrentStepValid == isCurrentStepValid &&
           other.name == name &&
           other.age == age &&
           other.theme == theme;
  }
  
  @override
  int get hashCode => Object.hash(currentStep, isCurrentStepValid, name, age, theme);
}