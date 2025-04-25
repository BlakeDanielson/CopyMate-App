# **Execution Plan: Sprint 2 \- Wizard Core & Photo Upload**

**Goal:** Implement the core multi-step wizard UI in Flutter, including steps for name, age, and theme selection. Implement the photo upload mechanism (UI, consent, backend endpoint for URL generation). Implement the backend logic for story creation orchestration (mocking AI calls) and necessary database models.

**Reference:** tech\_spec\_v1 (Latest Version); execution\_plan\_sprint1\_v1 (Previous Sprint)

**Phase 1 Continued: Backend Development (Ref: Weeds 2.x, 3.2, 3.4)**

1. **Task (Prep): Define Detailed API Contracts & DB Schema**  
   * **Action (Lead/All Devs):** BEFORE starting implementation, finalize and document the *exact* JSON structures for API endpoints relevant to Sprint 2 (Pre-signed URL, Story Creation Request/Response) and the detailed DB schema for photos, stories, story\_pages, orders tables (columns, types, constraints, indexes) in Notion or shared docs (Appendices 6.1, 6.2 of Tech Spec). *This unblocks parallel work.*  
2. **Task 2.6 & 4.2: Photo Model & Migration (TDD)**  
   * **Action (Backend):** Define Photo SQLAlchemy model based on finalized schema (user\_id, storage\_provider, bucket, key, filename, etc.). Define relevant Pydantic schemas.  
   * **Action (Backend \- Test First):** Write basic unit tests for the model definition/validation if applicable (e.g., Pydantic schema tests).  
   * **Action:** Run tests. **Verify they fail/pass** (as appropriate for schema tests).  
   * **Action (Code):** Implement the model and schemas.  
   * **Action:** Generate Alembic migration (alembic revision \--autogenerate \-m "Add photos table"). Review the generated script carefully.  
   * **Action:** Apply migration (alembic upgrade head).  
   * **Action:** Commit (feat(backend): implement photo model and migration).  
3. **Task 2.7: Pre-signed URL Endpoint (TDD)**  
   * **Action (Backend \- Test First):** Write integration tests (TestClient) for POST /v1/photos/upload-url:  
     * Test requires authentication (use protected route logic from Sprint 1).  
     * Test successful request returns a response containing URL and necessary fields (mock the boto3/google-cloud-storage client method).  
     * Test validation if any request body is needed (e.g., filename, content type).  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the FastAPI endpoint. Add cloud storage client dependency (boto3/google-cloud-storage). Implement logic to generate the pre-signed POST URL using the client library. Return the URL and required form fields (if using POST).  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up endpoint logic.  
   * **Action:** Commit (feat(backend): implement pre-signed URL generation endpoint with TDD).  
4. **Task 2.8 & 4.2: Story/StoryPage Models & Migration (TDD)**  
   * **Action (Backend):** Define Story and StoryPage SQLAlchemy models based on finalized schema (user\_id, title, prompt details, status, page number, text segment, image keys, etc.). Define Pydantic schemas for story creation input (wizard data) and basic story response.  
   * **Action (Backend \- Test First):** Write basic unit tests for model/schema definitions.  
   * **Action:** Run tests. **Verify they fail/pass.**  
   * **Action (Code):** Implement the models and schemas.  
   * **Action:** Generate Alembic migration (alembic revision \--autogenerate \-m "Add stories and story\_pages tables"). Review script.  
   * **Action:** Apply migration (alembic upgrade head).  
   * **Action:** Commit (feat(backend): implement story and story\_page models and migration).  
5. **Task 2.11 & 4.2: Order Model & Migration (Basic \- TDD)**  
   * **Action (Backend):** Define basic Order SQLAlchemy model based on finalized schema (user\_id, story\_id, status, amount, currency, stripe ID, POD ID, etc.). Define basic Pydantic schema. *Focus on fields needed for initial creation/linking.*  
   * **Action (Backend \- Test First):** Write basic unit tests for model/schema definitions.  
   * **Action:** Run tests. **Verify they fail/pass.**  
   * **Action (Code):** Implement the model and schema.  
   * **Action:** Generate Alembic migration (alembic revision \--autogenerate \-m "Add orders table"). Review script.  
   * **Action:** Apply migration (alembic upgrade head).  
   * **Action:** Commit (feat(backend): implement basic order model and migration).  
6. **Task 2.9: Core Story Creation Endpoint Logic \- Mocked AI (TDD)**  
   * **Action (Backend \- Test First):** Write integration tests (TestClient) for POST /v1/stories focusing on orchestration *without* actual AI calls:  
     * Test endpoint validation for wizard data (name, age, theme, photo ref).  
     * Test successful request creates Story record with generating status (mock DB commit).  
     * Test successful request returns appropriate response (e.g., story ID, status 202 Accepted).  
     * **Crucially:** Test that the endpoint *triggers* background tasks (e.g., Celery tasks if using it, or calls mocked service functions) for Text Gen, Image Gen, Personalization. *Do not test the AI logic itself here, just that the calls are initiated.* Use mocking (unittest.mock.patch or similar).  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the FastAPI endpoint logic:  
     * Validate input using Pydantic schemas.  
     * Create initial Story record in DB with generating status.  
     * **(If using Celery):** Dispatch the first background task (e.g., text\_generation\_task.delay(story\_id, prompt\_data)).  
     * **(If not using Celery yet):** Call placeholder/mocked service functions representing the AI steps.  
     * Return 202 Accepted response with Story ID.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up endpoint logic.  
   * **Action:** Commit (feat(backend): implement story creation endpoint orchestration (mocked AI) with TDD).

**Phase 1 Continued: Frontend Development (Ref: Weeds 3.x)**

7. **Task 3.6: Implement Wizard UI Shell/Structure (TDD)**  
   * **Action (Frontend \- Test First):** Write widget tests (flutter\_test) for the main Wizard screen/widget:  
     * Test that it displays a structure capable of holding steps (e.g., contains a Stepper, PageView, or custom step container).  
     * Test that it shows the correct initial step (e.g., Welcome or Name input).  
     * Test basic navigation between steps (Next/Back buttons \- disabled appropriately). Mock the wizard state notifier/bloc.  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the main Wizard widget (WizardScreen). Use a Stepper, PageView, or similar to manage steps. Connect Next/Back buttons to the WizardStateNotifier/WizardBloc to control the current step index/state. Display the placeholder widget for the first step.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up widget code.  
   * **Action:** Commit (feat(frontend): implement wizard multi-step shell with TDD).  
8. **Task 3.8, 3.9, 3.10: Implement Wizard Steps (Name, Age, Theme) (TDD)**  
   * **Action (Frontend \- Test First):** For *each* step (Name Input, Age Selection, Theme Selection):  
     * Write widget tests verifying the correct UI elements render (TextField, ChoiceChip, Cards).  
     * Test user interaction updates the WizardStateNotifier/WizardBloc state correctly (mock the notifier/bloc).  
     * Test input validation (e.g., name not empty) if applicable at the widget level.  
   * **Action:** Run tests for each step. **Verify they fail.**  
   * **Action (Code):** Implement the individual widgets for each step. Connect their interactions (onChanged, onTap, onSelected) to methods/events on the WizardStateNotifier/WizardBloc. Update the Wizard Shell (Task 7\) to display these actual step widgets based on the current step state.  
   * **Action:** Run tests for each step. **Verify they pass.**  
   * **Action (Refactor):** Clean up step widget code.  
   * **Action:** Commit (feat(frontend): implement wizard steps for name, age, theme with TDD).  
9. **Task 3.11: Implement Photo Upload Step UI & Backend Call (TDD)**  
   * **Action (Frontend \- Test First):** Write widget tests for the Photo Upload step widget:  
     * Test consent checkbox must be checked before upload button is enabled.  
     * Test upload button tap triggers interaction with a mocked PhotoUploadService or the WizardStateNotifier/WizardBloc.  
     * Test display of loading/progress state during mocked upload.  
     * Test display of success (e.g., thumbnail preview) or error message based on mocked service response.  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the Photo Upload widget UI (Checkbox, ElevatedButton, progress indicator, preview area).  
   * **Action (Code):** Implement the logic within the WizardStateNotifier/WizardBloc or a dedicated service:  
     1. On button tap (if consent checked): Call the backend API (POST /v1/photos/upload-url) via the ApiClientService (mocked for unit tests).  
     2. On successful response: Use image\_picker/file\_picker (mocked for unit tests) to let the user select a file.  
     3. **(Mocked Upload):** For now, simulate the upload process based on the pre-signed URL info received. Update state to show progress/success/failure. Store a reference/identifier for the "uploaded" photo in the wizard state. *Actual direct-to-cloud upload implementation deferred.*  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up photo upload logic/widget.  
   * **Action:** Commit (feat(frontend): implement photo upload step UI and pre-signed URL call with TDD (mocked upload)).  
10. **Task 3.12: Implement Generate Button Logic (TDD)**  
    * **Action (Frontend \- Test First):** Write widget tests for the final wizard step / generate button:  
      * Test button is enabled only when all required wizard steps (Name, Age, Theme, Photo Ref) are complete (check state).  
      * Test button tap calls the WizardStateNotifier/WizardBloc's submitStory method (or similar).  
      * Test UI transitions to loading state when submission starts.  
      * Test navigation to Story Preview screen (or error display) based on mocked API response from the submitStory method.  
    * **Action:** Run tests. **Verify they fail.**  
    * **Action (Code):** Implement the final step's UI logic. Implement the submitStory method in the WizardStateNotifier/WizardBloc:  
      * Gather all data from the wizard state.  
      * Call the backend API (POST /v1/stories) via the ApiClientService (mocked for unit tests).  
      * Update state based on API call (loading, success \+ story ID, error).  
      * Trigger navigation on success.  
    * **Action:** Run tests. **Verify they pass.**  
    * **Action (Refactor):** Clean up submission logic.  
    * **Action:** Commit (feat(frontend): implement generate story button and submission logic with TDD).

**Next Steps (Sprint 3 Focus):**

* Backend: Implement actual AI client calls within background tasks (Text Gen, Image Gen, Personalization). Implement Story/Order retrieval endpoints fully. Implement Stripe webhook handler logic. Implement POD order submission logic.  
* Frontend: Implement Story Preview screen (fetching data). Implement basic Checkout UI flow (connecting to backend Payment Intent). Implement Order History screen. Implement actual direct-to-cloud photo upload using pre-signed URL.  
* Ops: Set up Celery workers deployment. Refine monitoring.

Sprint 2 gets the core user input flow built and tested on both ends, ready for the real AI magic and checkout process in the next sprint. Keep hammering away.