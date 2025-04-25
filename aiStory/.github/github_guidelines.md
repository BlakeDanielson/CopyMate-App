# Standard Git Workflow

This document outlines a standard Git branching strategy and workflow suitable for many projects.

## Gitflow Branching Strategy

This project follows the Gitflow branching model, which provides a robust framework for managing larger projects with scheduled releases.

### Main Branches

-   **main** (formerly master): The main branch contains production-ready code. All code in this branch has been thoroughly tested and can be deployed to production at any time.
-   **develop**: The development branch serves as an integration branch for features. It contains code that will be included in the next release.

### Supporting Branches

-   **feature/***: Feature branches are used to develop new features. They branch off from `develop` and merge back into `develop` when the feature is complete.
-   **release/***: Release branches support preparation of a new production release. They branch off from `develop` and merge into `main` and `develop` when the release is complete.
-   **hotfix/***: Hotfix branches are used to quickly patch production releases. They branch off from `main` and merge into both `main` and `develop` when the fix is complete.

### Branch Naming Conventions

-   Feature branches: `feature/<feature-name>` or `feature/<ticket-id>-<brief-description>` (Link to task ID preferred)
-   Release branches: `release/v<major>.<minor>.<patch>` (e.g., `release/v1.0.0`)
-   Hotfix branches: `hotfix/v<major>.<minor>.<patch+1>` (e.g., `hotfix/v1.0.1`) or `hotfix/<brief-description>`

## Workflow

### Feature Development Workflow

1.  Create a feature branch from `develop`:
    ```bash
    git checkout develop
    git pull origin develop
    git checkout -b feature/my-feature
    ```
2.  Develop the feature with regular commits (following TDD principles where applicable):
    ```bash
    # Write test(s)
    # Run tests (fail)
    # Write code
    # Run tests (pass)
    # Refactor
    git add .
    git commit -m "feat: Meaningful commit message (Ticket: TASK-123)"
    ```
3.  Push the feature branch to remote frequently:
    ```bash
    git push origin feature/my-feature
    ```
4.  When the feature is complete (passes tests, meets Definition of Done), create a pull request (PR) to merge into `develop`.
5.  After code review and automated checks pass, merge the pull request.

### Release Workflow

1.  Create a release branch from `develop` when ready to release (feature complete for the release):
    ```bash
    git checkout develop
    git pull origin develop
    git checkout -b release/v1.0.0
    ```
2.  Make only bug fixes, documentation generation, and other release-oriented tasks in this branch. *No new features.*
3.  When the release is ready (tested, QA sign-off), merge into both `main` and `develop`:
    ```bash
    # Merge into main
    git checkout main
    git pull origin main
    git merge --no-ff release/v1.0.0
    git tag -a v1.0.0 -m "Version 1.0.0 Release"
    git push origin main --tags # Push main branch and the new tag

    # Merge back into develop to ensure develop has release fixes
    git checkout develop
    git pull origin develop
    git merge --no-ff release/v1.0.0
    git push origin develop

    # Clean up remote release branch (optional, depends on team policy)
    # git push origin --delete release/v1.0.0
    ```
4.  Delete the local release branch (`git branch -d release/v1.0.0`).

### Hotfix Workflow

1.  Create a hotfix branch from `main` (tag of the affected version is better if available):
    ```bash
    git checkout main # or git checkout v1.0.0
    git pull origin main
    git checkout -b hotfix/v1.0.1 # or hotfix/fix-critical-bug
    ```
2.  Fix the issue with necessary commits.
3.  When the fix is complete and verified, merge into both `main` and `develop`:
    ```bash
    # Merge into main
    git checkout main
    git pull origin main
    git merge --no-ff hotfix/v1.0.1
    git tag -a v1.0.1 -m "Version 1.0.1 Hotfix"
    git push origin main --tags

    # Merge back into develop
    git checkout develop
    git pull origin develop
    git merge --no-ff hotfix/v1.0.1
    git push origin develop

    # Clean up remote hotfix branch (optional)
    # git push origin --delete hotfix/v1.0.1
    ```
4.  Delete the local hotfix branch (`git branch -d hotfix/v1.0.1`).

## Pull Request (PR) Guidelines

-   All changes destined for `develop` and `main` **must** go through a Pull Request.
-   PRs require at least one code review approval from another team member (or as defined by team policy).
-   Automated CI checks (linters, **tests**) **must pass** before a PR can be merged.
-   Provide a clear description in the PR:
    * What problem does it solve?
    * What changes were made?
    * How was it tested?
    * Link to the relevant Task ID (e.g., Notion, Jira).
    * Screenshots/GIFs for UI changes.

## Tagging Strategy

-   Release versions follow Semantic Versioning (MAJOR.MINOR.PATCH).
-   Every merge into `main` that constitutes a release (including hotfixes) **must** be tagged.
-   Tag format: `vMAJOR.MINOR.PATCH` (e.g., `v1.0.0`, `v1.0.1`). Use annotated tags (`git tag -a`).

## CI/CD Integration

The Gitflow strategy integrates with a CI/CD pipeline (e.g., GitHub Actions, GitLab CI) as follows:

-   **Feature branches (`feature/*`)**: On push/PR -> Run linters, build checks, **unit & integration tests**.
-   **Develop branch**: On merge -> Run linters, all tests -> Build artifacts (e.g., Docker image, Web app) -> Deploy to **Staging Environment**.
-   **Main branch**: On merge (from release/hotfix) / Tag push -> Run linters, all tests -> Build artifacts -> Deploy to **Production Environment**.

## Best Practices

-   Keep feature branches focused and reasonably short-lived. Aim to merge back to `develop` frequently.
-   Regularly update your feature branch with the latest changes from `develop` (`git pull origin develop` then `git rebase develop` or `git merge develop` - team preference, but be consistent).
-   Write clear, concise commit messages using conventional commit format (e.g., `feat: ...`, `fix: ...`, `test: ...`, `refactor: ...`). Include Task ID in the commit body or footer.
-   Ensure local tests pass before pushing code.