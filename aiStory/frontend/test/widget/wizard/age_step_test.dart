import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ai_story/features/wizard/domain/models/wizard_state.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_state_notifier.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_providers.dart';
import 'package:ai_story/features/wizard/presentation/widgets/age_step.dart';

// Create a mock class for WizardStateNotifier
class MockWizardStateNotifier extends Mock implements WizardStateNotifier {}

void main() {
  group('AgeStep Widget Tests', () {
    late MockWizardStateNotifier mockWizardStateNotifier;
    late StateNotifierProvider<WizardStateNotifier, WizardState> mockWizardProvider;

    setUp(() {
      mockWizardStateNotifier = MockWizardStateNotifier();
      mockWizardProvider = StateNotifierProvider<WizardStateNotifier, WizardState>((ref) {
        return mockWizardStateNotifier;
      });

      // Set up default state with age 8
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 1, age: 8)
      );
    });

    testWidgets('AgeStep renders with age selection UI', (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: AgeStep(),
            ),
          ),
        ),
      );

      // Assert - Verify the slider is present
      expect(find.byType(Slider), findsOneWidget);
      
      // Verify there's an instructional text
      expect(find.text('How old is your character?'), findsOneWidget);
      
      // Verify the current age is displayed
      expect(find.text('8 years old'), findsOneWidget);
    });

    testWidgets('Slider updates age in WizardState when changed', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: AgeStep(),
            ),
          ),
        ),
      );

      // Find the slider
      final slider = find.byType(Slider);
      
      // Act - Drag the slider to update age (middle of slider should be about age 10)
      await tester.drag(slider, const Offset(50.0, 0.0));
      await tester.pumpAndSettle();
      
      // Verify updateAge was called
      verify(() => mockWizardStateNotifier.updateAge(any())).called(1);
    });

    testWidgets('Age category chips update age when selected', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: AgeStep(),
            ),
          ),
        ),
      );

      // Find the "Teen" category chip
      final teenChip = find.widgetWithText(ChoiceChip, 'Teen');
      expect(teenChip, findsOneWidget);
      
      // Act - Tap the teen chip
      await tester.tap(teenChip);
      await tester.pumpAndSettle();
      
      // Verify updateAge was called with 13 (typical teen age)
      verify(() => mockWizardStateNotifier.updateAge(13)).called(1);
    });

    testWidgets('Initial age is reflected in the UI', (WidgetTester tester) async {
      // Arrange - Set up state with a different age
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 1, age: 15)
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: AgeStep(),
            ),
          ),
        ),
      );

      // Assert - Verify displayed age matches state
      expect(find.text('15 years old'), findsOneWidget);
    });
  });
}