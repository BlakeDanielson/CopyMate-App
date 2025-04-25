# GuardianLens Git Workflow

This document outlines the Git branching strategy and workflow for the GuardianLens project.

## Gitflow Branching Strategy

The GuardianLens project follows the Gitflow branching model, which provides a robust framework for managing larger projects with scheduled releases.

### Main Branches

- **main** (formerly master): The main branch contains production-ready code. All code in this branch has been thoroughly tested and can be deployed to production at any time.
- **develop**: The development branch serves as an integration branch for features. It contains code that will be included in the next release.

### Supporting Branches

- **feature/***:  Feature branches are used to develop new features. They branch off from develop and merge back into develop when the feature is complete.
- **release/***:  Release branches support preparation of a new production release. They branch off from develop and merge into main and develop when the release is complete.
- **hotfix/***:  Hotfix branches are used to quickly patch production releases. They branch off from main and merge into both main and develop when the fix is complete.

### Branch Naming Conventions

- Feature branches: `feature/<feature-name>` or `feature/<ticket-id>-<brief-description>`
- Release branches: `release/v<major>.<minor>.<patch>` (e.g., `release/v1.0.0`)
- Hotfix branches: `hotfix/v<major>.<minor>.<patch+1>` (e.g., `hotfix/v1.0.1`) or `hotfix/<brief-description>`

## Workflow

### Feature Development Workflow

1. Create a feature branch from develop:
   ```
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-feature
   ```

2. Develop the feature with regular commits:
   ```
   git add .
   git commit -m "Meaningful commit message"
   ```

3. Push the feature branch to remote:
   ```
   git push origin feature/my-feature
   ```

4. When the feature is complete, create a pull request to merge into develop.
5. After code review and testing, merge the pull request.

### Release Workflow

1. Create a release branch from develop when ready to release:
   ```
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.0.0
   ```

2. Make only bug fixes and release preparation changes in this branch.
3. When the release is ready, merge into both main and develop:
   ```
   git checkout main
   git pull origin main
   git merge --no-ff release/v1.0.0
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin main --tags
   
   git checkout develop
   git pull origin develop
   git merge --no-ff release/v1.0.0
   git push origin develop
   ```

4. Delete the release branch.

### Hotfix Workflow

1. Create a hotfix branch from main:
   ```
   git checkout main
   git pull origin main
   git checkout -b hotfix/v1.0.1
   ```

2. Fix the issue with necessary commits.
3. When the fix is complete, merge into both main and develop:
   ```
   git checkout main
   git pull origin main
   git merge --no-ff hotfix/v1.0.1
   git tag -a v1.0.1 -m "Version 1.0.1"
   git push origin main --tags
   
   git checkout develop
   git pull origin develop
   git merge --no-ff hotfix/v1.0.1
   git push origin develop
   ```

4. Delete the hotfix branch.

## Pull Request Guidelines

- All changes to develop and main must go through a pull request
- Pull requests require at least one code review approval
- Automated tests must pass before a pull request can be merged
- Provide a clear description of changes in the pull request

## Tagging Strategy

- Release versions follow semantic versioning (MAJOR.MINOR.PATCH)
- Every release to main must be tagged with its version number
- Tag format: v1.0.0

## CI/CD Integration

The Gitflow strategy integrates with our CI/CD pipeline as follows:

- **Feature branches**: Run builds and tests
- **Develop branch**: Deploy to staging environment
- **Main branch**: Deploy to production environment

## Best Practices

- Keep feature branches short-lived
- Regularly merge/rebase with develop to minimize conflicts
- Write clear, concise commit messages
- Reference ticket IDs in branch names and commit messages where applicable