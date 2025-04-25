#!/bin/bash

# Script to add project directories to the monorepo while respecting existing Git repos

# List of projects to skip completely (if any)
SKIP_PROJECTS=()

# Function to check if a project should be skipped
should_skip() {
  local project=$1
  for skip_project in "${SKIP_PROJECTS[@]}"; do
    if [[ "$project" == "$skip_project" ]]; then
      return 0
    fi
  done
  return 1
}

# Get all directories in the current folder
for project in */; do
  # Remove trailing slash
  project=${project%/}
  
  # Skip hidden directories and those in the skip list
  if [[ "$project" == .* ]] || should_skip "$project"; then
    echo "Skipping $project"
    continue
  fi
  
  echo "Processing project: $project"
  
  # Check if the project has its own Git repository
  if [ -d "$project/.git" ]; then
    echo "$project has its own Git repository. Handling specially..."
    
    # Option 1: Add as is (ignoring the .git directory)
    echo "Adding $project files to monorepo (excluding .git directory)..."
    git add "$project"
    
    # Option 2 (Alternative): If you want to preserve the project's Git history,
    # you would use Git submodules instead, which would involve running:
    # git submodule add <repo-url> $project
    # But this requires the project to already be in a remote repository
  else
    echo "Adding $project to monorepo..."
    git add "$project"
  fi
done

echo "All projects processed. Please review the changes and commit them."
echo "You can use: git commit -m \"Add all projects to monorepo\"" 