# BlakeProjects Monorepo Setup

This document explains how the BlakeProjects monorepo is structured and how to handle moving between your local environment and GitHub.

## Repository Structure

This repository is set up as a monorepo containing multiple independent projects. Each project has its own directory and may already have its own Git history.

## Handling Nested Git Repositories

Many of the projects in this monorepo already have their own Git repositories. There are two main approaches to handle this:

### Option 1: Simple Directory Storage (Current Approach)

In this approach, we are simply storing the project directories in the monorepo, while ignoring their individual `.git` directories. This means:

- The monorepo doesn't track the individual Git history of each project
- Changes to projects will be tracked in the monorepo going forward
- The original repositories remain unchanged and can be used separately

This is the simpler approach and is suitable if you mainly want to backup and organize your projects.

### Option 2: Git Submodules (Advanced Alternative)

Alternatively, you could convert the projects to Git submodules. This would:

- Link to the original repositories rather than copying their content
- Preserve the full Git history of each project
- Allow you to work with each project's repository independently
- Require more complex Git operations when updating

To convert a project to a submodule, you would:
1. Remove the project files from the monorepo
2. Add the project as a submodule: `git submodule add <repository-url> <project-directory>`

## Adding New Projects

To add a new project to the monorepo:

1. Create the project directory inside the monorepo
2. Add the project files
3. Commit the changes: `git add <project-directory> && git commit -m "Add new project: <project-name>"`
4. Push the changes: `git push origin main`

## Moving the Repository

If you need to transfer this repository to a new machine:

1. Clone the repository: `git clone https://github.com/BlakeDanielson/BlakeProjects.git`
2. Navigate to the repository: `cd BlakeProjects`
3. Start working with your projects

## Important Notes

- The `.gitignore` file is set up to ignore the `.git` directories of sub-projects
- Large binary files and build artifacts are also ignored to keep the repository size manageable
- Each project may have its own dependencies and setup requirements 