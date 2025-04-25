# **Execution Plan: Sprint 0 - Foundation Setup**

**Goal:** Establish the project structure, core tooling, local development environment, and implement the first basic, tested backend endpoint.

**Reference:** tech\_spec\_weeds\_v1 Sections 1 & 2 (Initial Tasks)

**Phase 1 Kick-off: Common Setup & Tooling (Ref: Weeds 1.x)**

1. **Task 1.1: Git Repository Setup**
   * **Action:** Initialize Git repository. Choose Monorepo structure (Recommended).
   * **Commands (Monorepo Example):**
     ```bash
     git init ai-story-creator
     cd ai-story-creator
     mkdir frontend backend
     touch README.md .gitignore
     # Add standard Node.js/Flutter and Python .gitignore rules
     git add .
     git commit -m "Initial project structure setup"
     # Push to your remote (GitHub/GitLab/etc.)
     ```

   * **Action:** Define Branching Strategy (Gitflow Lite Recommended: main, develop, feature/your-feature-name). Document this briefly in the README.md or Notion.
   * **Action:** Set up PR Template (in .github/pull\_request\_template.md or equivalent). Require: Description, Linked Notion Task ID, Testing Done, Screenshots (if UI). Define required reviewers (e.g., at least one other team member).
2. **Task 1.2: Notion Project Setup**
   * **Action:** Create Notion Database/Board for tasks.
   * **Action:** Define Columns/Statuses: To Do, In Progress, Blocked, Code Review, QA Ready, Done.
   * **Action:** Define Task Template Fields: Assignee, Sprint (e.g., Sprint 0), Status, Priority, Story Points (optional), Link to Spec Task \#, Link to PR.
   * **Action:** Populate with initial tasks from tech\_spec\_weeds\_v1 for Phase 1. Assign owners.
3. **Task 1.5: Backend Dependency Management Choice**
   * **Decision:** Use Poetry for dependency management.
     * Poetry: Robust dependency resolution, locking, virtual env management built-in. Better for managing complex dependencies long-term.
   * **Action:** Document the chosen method in the backend README.md.
4. **Task 1.6: IDE & Linter Setup**
   * **Action (Backend):**
     * Create backend/.venv (python -m venv .venv). Activate it.
     * pip install black isort flake8 pytest pytest-asyncio
     * Configure VS Code (or other IDE) Python interpreter to use .venv.
     * Configure format-on-save using black and isort. Add setup.cfg or pyproject.toml for flake8 config (e.g., ignore specific errors, set line length).
   * **Action (Frontend):**
     * Install recommended Flutter/Dart extensions for your IDE.
     * Configure format-on-save (dart format).
     * Review/customize frontend/analysis\_options.yaml for stricter linting rules if desired.
5. **Task 1.3: Local Docker Environment**
   * **Action (Backend):** Create backend/Dockerfile. Define steps to copy code, install dependencies (based on chosen method in Task 1.5), expose FastAPI port (e.g., 8000).
   * **Action:** Create docker-compose.yml in the project root:
     ```yaml
     # docker-compose.yml (Example)
     version: '3.8'
     services:
       db:
         image: postgres:16
         volumes:
           - postgres\_data:/var/lib/postgresql/data/
         environment:
           POSTGRES\_DB: story\_creator\_db
           POSTGRES\_USER: user
           POSTGRES\_PASSWORD: password # Use secrets in real setup
         ports:
           - "5432:5432" # Map only if needed locally outside Docker

       backend:
         build: ./backend # Points to the directory with Dockerfile
         command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload # Example command
         volumes:
           - ./backend:/app # Mount local code for hot-reloading
         ports:
           - "8000:8000"
         environment:
          AISTORY\_DATABASE\_URL: postgresql+asyncpg://user:password@db:5432/story\_creator\_db
          AISTORY\_DEBUG: "true"  # Enable debug mode
          # Add other necessary ENV VARS (JWT\_SECRET, etc.)
        depends\_on:
          - db

     volumes:
       postgres\_data:
     ```

   * **Action:** Test the setup: docker-compose up --build. Verify containers start and backend is accessible.

**Phase 1 Kick-off: Backend Basics (Ref: Weeds 2.x - Initial Tasks)**

6. **Task 2.1: Initialize FastAPI Project**
   * **Action (Backend):** Create backend/main.py. Initialize FastAPI app instance (app = FastAPI()). Set up basic config loading (e.g., pydantic-settings). Create initial pyproject.toml with fastapi, uvicorn[standard], pydantic-settings. Install them (poetry install).
7. **Task 2.2: Implement /health Endpoint (TDD)**
   * **Action (Backend - Test First):** Create backend/tests/test\_main.py. Write the first test:
     ```python
     # backend/tests/test\_main.py (Example)
     from fastapi.testclient import TestClient
     # Assuming your app instance is in main.py
     # Adjust import path as needed
     from main import app

     client = TestClient(app)

     def test\_health\_check():
         response = client.get("/health")
         assert response.status\_code == 200
         assert response.json() == {"status": "ok"}
     ```

   * **Action:** Run the test (pytest backend/tests). **Verify it fails** (404 Not Found).
   * **Action (Code):** Implement the endpoint in backend/main.py:
     ```python
     # backend/main.py (Additions)
     from fastapi import FastAPI

     app = FastAPI()
     # ... other setup ...

     @app.get("/health")
     async def health\_check():
         return {"status": "ok"}
     ```

   * **Action:** Run the test again (pytest backend/tests). **Verify it passes.**
   * **Action (Refactor):** Review the code. Is it clean? (For this simple case, probably yes).
   * **Action:** Commit the changes (git add ., git commit -m "feat(backend): add /health endpoint with TDD").

**Next Steps:**

* Continue TDD cycle for Backend Task 2.3 (DB Setup/Connection Test).
* Start Frontend Task 3.1 (Initialize Flutter Project).
* Define initial API Contracts (Appendix 6.1) and DB Schema (Appendix 6.2) in more detail in Notion or shared docs *before* implementing dependent tasks.

This gives you concrete steps to get the ball rolling. Tackle these one by one. Remember the TDD rhythm: Red -> Green -> Refactor. Commit often. Keep Notion updated. Let me know when you're ready to break down the *next* chunk of tasks. We'll get this beast built.