# IDE and Linter Setup

This document outlines the steps to set up your IDE and linters for the AI Story Creator project.

## Backend Setup (Python)

### Prerequisites

*   Python 3.10+
*   Poetry

### Steps

1.  **Create a virtual environment:**

    ```bash
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**

    ```bash
    pip install black isort flake8 pytest pytest-asyncio
    ```

3.  **Configure VS Code:**

    *   Create a `.vscode` directory in the `backend` directory.
    *   Create a `settings.json` file in the `.vscode` directory with the following content:

        ```json
        {
            "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
            "python.formatting.provider": "black",
            "python.formatting.blackPath": "${workspaceFolder}/.venv/bin/black",
            "python.linting.enabled": true,
            "python.linting.flake8Enabled": true,
            "python.linting.flake8Path": "${workspaceFolder}/.venv/bin/flake8",
            "python.linting.pylintEnabled": false,
            "python.linting.mypyEnabled": true,
            "python.linting.mypyPath": "${workspaceFolder}/.venv/bin/mypy",
            "python.sortImports.path": "${workspaceFolder}/.venv/bin/isort",
            "[python]": {
                "editor.formatOnSave": true,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": true
                },
                "editor.defaultFormatter": "ms-python.python"
            },
            "editor.rulers": [88],
            "files.exclude": {
                "**/__pycache__": true,
                "**/*.pyc": true
            }
        }
        ```

4.  **Configure Flake8:**

    *   Add the following configuration to your `pyproject.toml` file:

        ```toml
        [tool.flake8]
        max-line-length = 88
        extend-ignore = "E203, W503"
        exclude = [
            ".git",
            "__pycache__",
            ".venv",
            "alembic",
        ]
        ```

## Frontend Setup (Flutter)

### Prerequisites

*   Flutter SDK
*   Dart SDK

### Steps

1.  **Install Flutter/Dart extensions in VS Code.**
2.  **Configure VS Code:**

    *   Create a `.vscode` directory in the `frontend` directory.
    *   Create a `settings.json` file in the `.vscode` directory with the following content:

        ```json
        {
            "editor.formatOnSave": true,
            "editor.formatOnType": true,
            "editor.rulers": [
                80
            ],
            "editor.codeActionsOnSave": {
                "source.fixAll": true,
                "source.organizeImports": true
            },
            "dart.lineLength": 80,
            "dart.previewFlutterUiGuides": true,
            "dart.previewFlutterUiGuidesCustomTracking": true,
            "dart.openDevTools": "flutter",
            "dart.debugExternalPackageLibraries": false,
            "dart.debugSdkLibraries": false,
            "[dart]": {
                "editor.formatOnSave": true,
                "editor.formatOnType": true,
                "editor.selectionHighlight": false,
                "editor.suggest.snippetsPreventQuickSuggestions": false,
                "editor.suggestSelection": "first",
                "editor.tabCompletion": "onlySnippets",
                "editor.wordBasedSuggestions": "off",
                "editor.defaultFormatter": "Dart-Code.dart-code"
            },
            "files.exclude": {
                "**/.dart_tool": true,
                "**/.flutter-plugins": true,
                "**/.flutter-plugins-dependencies": true,
                "**/*.g.dart": false,
                "**/*.freezed.dart": false
            }
        }
        ```

3.  **Configure Linting Rules:**

    *   Create an `analysis_options.yaml` file in the `frontend` directory with the following content:

        ```yaml
        # This file configures the analyzer to use the lint rule set from `package:flutter_lints`
        # and defines customizations for stricter linting rules.

        include: package:flutter_lints/flutter.yaml

        analyzer:
          exclude:
            - "**/*.g.dart"
            - "**/*.freezed.dart"
          errors:
            invalid_annotation_target: ignore
          language:
            strict-casts: true
            strict-raw-types: true

        linter:
          rules:
            # Error rules
            avoid_empty_else: true
            avoid_relative_lib_imports: true
            avoid_returning_null_for_future: true
            avoid_types_as_parameter_names: true
            no_duplicate_case_values: true
            unrelated_type_equality_checks: true
            valid_regexps: true

            # Style rules
            always_declare_return_types: true
            always_require_non_null_named_parameters: true
            annotate_overrides: true
            avoid_multiple_declarations_per_line: true
            avoid_unnecessary_containers: true
            avoid_unused_constructor_parameters: true
            prefer_const_constructors: true
            prefer_const_declarations: true
            prefer_final_fields: true
            prefer_final_locals: true
            prefer_interpolation_to_compose_strings: true
            prefer_single_quotes: true
            sort_child_properties_last: true

            # Flutter rules
            use_build_context_synchronously: true
            use_full_hex_values_for_flutter_colors: true
            use_key_in_widget_constructors: true

            # Additional rules
            avoid_print: true
            prefer_relative_imports: true
            avoid_void_async: true
            no_logic_in_create_state: true
            prefer_void_to_null: true