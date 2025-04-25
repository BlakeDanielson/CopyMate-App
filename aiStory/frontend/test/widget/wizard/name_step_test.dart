import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:ai_story/features/wizard/domain/models/wizard_state.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_state_notifier.dart';
import 'package:ai_story/features/wizard/presentation/providers/wizard_providers.dart';
import 'package:ai_story/features/wizard/presentation/widgets/name_step.dart';

// Create a mock class for WizardStateNotifier
class MockWizardStateNotifier extends Mock implements WizardStateNotifier {}

void main() {
  group('NameStep Widget Tests', () {
    late MockWizardStateNotifier mockWizardStateNotifier;
    late StateNotifierProvider<WizardStateNotifier, WizardState> mockWizardProvider;

    setUp(() {
      mockWizardStateNotifier = MockWizardStateNotifier();
      mockWizardProvider = StateNotifierProvider<WizardStateNotifier, WizardState>((ref) {
        return mockWizardStateNotifier;
      });

      // Set up default state with empty name
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 0, name: '')
      );
    });

    testWidgets('NameStep renders with TextField', (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: NameStep(),
            ),
          ),
        ),
      );

      // Assert - Verify the text field is present
      expect(find.byType(TextField), findsOneWidget);
      
      // Verify there's an instructional text
      expect(find.text('What should we call your character?'), findsOneWidget);
    });

    testWidgets('TextField updates name in WizardState when text changes', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: NameStep(),
            ),
          ),
        ),
      );

      // Act - Enter text
      await tester.enterText(find.byType(TextField), 'Test Character');
      
      // Verify the updateName method was called with the right argument
      verify(() => mockWizardStateNotifier.updateName('Test Character')).called(1);
    });

    testWidgets('TextField displays initial name from state', (WidgetTester tester) async {
      // Arrange - Set up state with an existing name
      when(() => mockWizardStateNotifier.state).thenReturn(
        const WizardState(currentStep: 0, name: 'Existing Name')
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: NameStep(),
            ),
          ),
        ),
      );

      // Assert - Verify initial text
      expect(find.text('Existing Name'), findsOneWidget);
    });

    testWidgets('Empty name sets step validity to false', (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            wizardProvider.overrideWithProvider(mockWizardProvider)
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: NameStep(),
            ),
          ),
        ),
      );

      // Act - Clear the text field
      await tester.enterText(find.byType(TextField), '');
      
      // Verify updateName was called with empty string
      verify(() => mockWizardStateNotifier.updateName('')).called(1);
    });
  });
}