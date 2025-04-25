# **Getting In The Weeds - AI Story Creator Tech Spec**

**Purpose:** This document identifies specific areas within the main Technical Specification (tech\_spec\_v1) that require further detailed definition, clarification, or decision-making before or during Phase 1 implementation. It serves as a checklist for deep dives.

**1. Common Setup & Tooling (Section 3.1)**

*   **Task 1.1 (Git Strategy):** Define specific branch naming conventions (e.g., feature/, bugfix/, release/), PR template requirements, and required reviewers/approval processes.
*   **Task 1.2 (Notion Workflow):** Detail the Notion task states (e.g., To Do, In Progress, In Review, QA, Done), required fields per task (Assignee, Sprint, Story Points?), and linking strategy between tasks, epics, and potentially design docs/ADRs.
*   **Task 1.5 (Dependency Management - BE):** Use Poetry for managing Python dependencies and lock files. Document the chosen process.
*   **Task 1.6 (IDE Setup):** Specify required linters/formatters (e.g., black, isort, flake8 for Python; dart format, dart analyze with specific analysis\_options.yaml rules for Flutter) and IDE extensions to enforce consistency. Also, ensure all team members configure their IDEs to use the project's virtual environment.

**2. Backend Development (Section 3.2)**
*   **Task 1.3 (Docker Environment):** Ensure the docker-compose.yml file is up-to-date with the correct environment variables (AISTORY\_DATABASE\_URL, AISTORY\_DEBUG) and that the Docker setup instructions are clear and concise.

*   **API Contract Definitions (Appendix 6.1):**
    *   **Critical Endpoints:** Define *exact* request/response JSON structures (including field names, data types, nullability) with examples for:
        *   POST /v1/auth/token (request/response, including token structure/expiry)
        *   POST /v1/users (signup request/response)
        *   POST /v1/photos/upload-url (request/response including URL format, fields for direct upload)
        *   POST /v1/stories (request body detailing wizard inputs, response body including story ID/status)
        *   GET /v1/stories/{story\_id} (response body detailing story pages, text, image keys)
        *   POST /v1/orders (request body, response including client secret)
        *   POST /v1/webhooks/stripe (expected event structure for payment\_intent.succeeded)
    *   **Error Responses:** Define a standard JSON structure for API error responses (e.g., {"detail": "Error message", "code": "ERROR\_CODE"}). List key ERROR\_CODEs.
*   **Database Schema (Appendix 6.2):**
    *   **Table Details:** For *each* table (users, photos, stories, story\_pages, orders), specify:
        *   Column names, exact PostgreSQL data types (VARCHAR(x), TEXT, INTEGER, TIMESTAMP WITH TIME ZONE, BOOLEAN, JSONB, UUID, etc.).
        *   Constraints: PRIMARY KEY, FOREIGN KEY relationships (with ON DELETE behavior - e.g., CASCADE, SET NULL), NOT NULL, UNIQUE.
        *   Indexes: Define necessary indexes beyond primary/foreign keys (e.g., on user\_id in stories/orders, on status fields, potentially GIN index for JSONB fields if queried).
*   **Task 2.5 (JWT Strategy):** Specify JWT token expiry duration (e.g., 15 mins for access, 7 days for refresh?). Define refresh token storage mechanism (secure HTTPOnly cookie? DB?) and rotation strategy.
*   **Task 2.9 (Story Orchestration - Error Handling):**
    *   Define specific error handling and state updates in the stories table for failures at each step: Text Gen API failure, Base Image Gen failure (per page?), Personalization failure (per page?).
    *   Define the *exact* fallback logic for personalization failure (e.g., Store null in personalized\_image\_key? Store base image key there? Add a personalization\_status field?).
    *   Define retry logic (how many times, backoff strategy) for transient AI API errors.
*   **Task 2.9 (Page Segmentation Logic):** Define the MVP algorithm for splitting generated text into pages (e.g., split by \\n\\n? Target word count per page?).
*   **Task 2.13 (Stripe Webhook Security):** Detail the signature verification implementation using the Stripe library and webhook secret.
*   **Task 2.14 (POD API Interaction):** Define the *exact* payload structure required by the chosen POD provider's API for order submission. Specify how image URLs (from S3/GCS) will be provided. Define how POD status updates (if available via webhook or polling) will update the orders table status.
*   **Task 2.16 (Logging Content):** Specify key information to log for critical events:
    *   API Request: Method, Path, User ID (if auth'd), Request Body (potentially redacted).
    *   API Response: Status Code, Response Time.
    *   Story Generation Start: User ID, Input Params (name, age, theme), Story ID.
    *   AI API Call: Service Name, Model, Request Prompt (or hash/ID), Response Status, Latency, Cost (if available).
    *   DB Query: Query (potentially simplified), Parameters, Latency.
    *   Errors: Full traceback, relevant context variables.

**3. Frontend Development (Section 3.3)**

*   **Task 3.2 (State Management Choice):** Finalize Riverpod vs. Bloc decision. Outline the *names* and *responsibilities* of key providers/blocs (e.g., AuthNotifier, WizardStateNotifier, StoryServiceProvider, OrderBloc). Define the core state properties managed by each.
*   **Task 3.3 (API Client Error Handling):** Define how dio interceptors will map backend HTTP error status codes (4xx, 5xx) and standard error JSON responses into specific Dart exceptions or state updates for the UI.
*   **Task 3.5 (Routing Details):** List all go\_router routes, their paths, associated screens/widgets, and any required parameters (e.g., /story/:storyId). Define redirect logic for auth guarding.
*   **Task 3.11 (Photo Upload Implementation):** Specify how platform differences between web (file\_picker) and native (image\_picker) will be handled. Detail the UI feedback during upload (progress indicator tied to pre-signed URL upload). Define max file size/resolution limits.
*   **Task 3.11 (Consent Wording):** Finalize the *exact* user-facing text for the photo upload consent checkbox and any linked privacy policy snippets.
*   **Task 3.12 (Loading State UI):** Specify the visual design and behavior of the loading indicator during story generation (e.g., simple spinner? Progress bar? Animated sequence?).
*   **Task 3.13 (Story Preview Widget):** Define the specific widget choice (PageView, CarouselSlider, custom?) and how text/images will be laid out per page. How will image loading/error states be handled *within* the preview?
*   **Task 3.14 (Stripe Integration):** Decide *how* Stripe Elements (or equivalent) will be integrated. Using stripe\_flutter package? A webview for Stripe Checkout? Custom UI calling backend for Payment Intent? Detail the chosen approach.
*   **Task 3.17 (Responsive Breakpoints):** Define specific screen width breakpoints (e.g., small \< 600dp, medium 600-840dp, large \> 840dp) and how the layout of key screens (Wizard, Preview, Dashboard) will adapt.

**4. AI Integration (Section 3.5)**

*   **Task 5.3 (MVP Prompt Templates):** Provide the *actual text* of the initial prompt templates for each theme/age combination, clearly showing placeholders for name/age/theme keywords.
*   **Task 5.4 (Replicate Model IDs):** List the specific Replicate model URLs/identifiers intended for use in MVP (e.g., stability-ai/sdxl:...?version=..., fofr/face-swap:...?version=...). Include fallback model ideas if primary choices prove unreliable.

**5. Security Implementation (Section 3.7)**

*   **Task 7.1 (JWT Details):** Specify access token expiry (e.g., 15 minutes), refresh token expiry (e.g., 7 days), and refresh mechanism details (e.g., endpoint path, request/response structure).
*   **Task 7.6 (Secrets Management Strategy):** Define *how* secrets will be injected into environments (e.g., Docker Compose env\_file locally, Render Environment Groups, Cloud Run Secret Manager integration).
*   **Task 7.7 (Rate Limiting Config):** Specify initial limits for slowapi (e.g., "5 requests per minute per IP" for /auth/token).
*   **Task 7.8 (CORS Origins):** List the specific frontend origins allowed for Dev, Staging, and Production environments.

**6. Deployment & CI/CD (Section 3.8)**

*   **Task 8.2 / 8.3 (CI/CD - Detailed Steps):**
    *   Specify exact lint/test commands to run (pytest -v, flutter test --coverage).
    *   Detail Docker build arguments/context.
    *   Specify deployment commands/scripts for target platforms (e.g., gcloud run deploy..., Render deploy hook details, static site deployment command).
    *   Define strategy for handling/passing secrets to CI/CD environment securely (e.g., GitHub Secrets).
    *   Add step for generating/uploading test coverage reports.

**7. Integration Testing & QA (Section 3.9)**

*   **Task 9.1 (Integration Test Scenarios):** List key end-to-end scenarios for Flutter integration\_test (e.g., "Signup -> Create Story (Theme A) -> Preview -> Start Checkout", "Login -> View Order History").
*   **Task 9.3 (Security Test Checklist - Detailed):** Expand the basic checklist: Test password reset flow security, check for insecure direct object references (IDORs) on API endpoints (can user A access user B's story?), verify cookie security flags if using cookies, check photo access controls directly on S3/GCS if possible.
*   **Task 9.4 (Quality Rubric):** Define basic criteria for evaluating generated story quality (e.g., Coherence: 1-5, Image Relevance: 1-5, Personalization Success: Y/N/Partial).