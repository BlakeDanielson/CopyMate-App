# **Execution Plan: Sprint 3 \- AI Integration & Core Loop**

**Goal:** Integrate actual AI services for text and image generation/personalization. Implement the story preview screen, the real photo upload to cloud storage, and the basic checkout flow (shipping, payment intent). Enable viewing order history.

**Reference:** tech\_spec\_v1 (Latest Version); execution\_plan\_sprint2\_v1 (Previous Sprint)

**Phase 1 Continued: Backend Development (Ref: Weeds 2.x, 3.2, 3.5, 3.6)**

1. **Task (Setup): Celery Integration (If not done, based on Task 2.11)**  
   * **Action (Backend):** Install Celery (celery\[redis\]). Configure Celery app instance, broker URL (Redis), backend (optional, e.g., Redis or DB). Integrate with FastAPI (e.g., using helper functions to dispatch tasks).  
   * **Action (Backend \- Test First):** Write tests verifying Celery tasks can be dispatched from FastAPI endpoints (mock task.delay()) and that basic worker setup connects (integration test with local Docker Compose Redis/Worker).  
   * **Action:** Run tests. **Verify they fail/pass.**  
   * **Action (Code):** Implement Celery configuration and integration points. Update docker-compose.yml to include a celery-worker service.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action:** Commit (feat(backend): integrate celery for background tasks).  
2. **Task 2.9 (Continued): Implement AI Calls in Background Tasks (TDD)**  
   * **Action (Backend):** Define Celery tasks (or async functions if not using Celery yet) for:  
     * text\_generation\_task(story\_id, prompt\_data)  
     * base\_image\_generation\_task(story\_page\_id, text\_segment)  
     * personalization\_task(story\_page\_id, base\_image\_key, photo\_ref)  
   * **Action (Backend \- Test First):** For *each* task:  
     * Write unit tests mocking the specific AI client (openai, replicate) and DB interactions.  
     * Test successful execution: Verify correct API parameters are sent, mocked successful AI response is processed, DB is updated correctly (e.g., story text saved, image keys saved, status updated).  
     * Test AI API error handling: Verify exceptions from mocked clients are caught, logged, and story/page status is updated appropriately (e.g., generation\_failed).  
     * Test Personalization Fallback: Specifically test the personalization\_task handling a failure from the mocked Replicate personalization call, ensuring it falls back correctly (e.g., uses base image key, updates status).  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the logic within each task:  
     * Fetch necessary data (e.g., story prompt, photo ref from DB).  
     * Initialize and call the actual AI client library (using keys from secure config).  
     * Process the response.  
     * Update the Story or StoryPage status and data in the database.  
     * Implement robust error handling and logging around API calls.  
     * Chain tasks appropriately (e.g., text gen finishes \-\> triggers image gen tasks \-\> image gen finishes \-\> triggers personalization tasks).  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up task logic.  
   * **Action:** Modify POST /v1/stories (Task 6 from Sprint 2\) to dispatch the *first* real Celery task (text\_generation\_task.delay(...)) instead of calling mocks. Update its integration tests.  
   * **Action:** Commit (feat(backend): implement AI generation background tasks with TDD).  
3. **Task 2.10 (Continued): Finalize Story Retrieval Endpoints (TDD)**  
   * **Action (Backend \- Test First):** Update integration tests (TestClient) for GET /v1/stories/{story\_id}:  
     * Test retrieving a story successfully *after* mocked background tasks have "completed" (manually set DB status/data for test setup). Verify response includes page text and image keys.  
     * Test retrieving a story still in generating status.  
     * Test retrieving a story where generation failed.  
   * **Action:** Run tests. **Verify they fail/pass** based on existing implementation.  
   * **Action (Code):** Refine the endpoint logic and SQLAlchemy queries to accurately reflect story/page status and return all necessary data for the preview screen. Ensure sensitive data isn't exposed.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up retrieval logic.  
   * **Action:** Commit (feat(backend): finalize story retrieval endpoints with TDD).  
4. **Task 2.13 (Continued): Implement Stripe Webhook Handler Logic (TDD)**  
   * **Action (Backend \- Test First):** Update/write integration tests (TestClient) for POST /v1/webhooks/stripe:  
     * Test payment\_intent.succeeded event: Verify order status is updated in DB (mocked). Verify it triggers the POD submission task/logic (mock task.delay() or service call).  
     * Test payment\_intent.payment\_failed event: Verify order status is updated appropriately (mocked DB).  
     * Test handling of events for unknown payment intents.  
     * Test signature verification logic thoroughly (using Stripe CLI locally or test vectors).  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the full logic inside the webhook handler based on event type. Update order status in the database. Trigger the POD task (Task 5 below).  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up webhook logic.  
   * **Action:** Commit (feat(backend): implement stripe webhook handler logic with TDD).  
5. **Task 2.14 (Continued): Implement POD Order Submission Task (TDD)**  
   * **Action (Backend):** Define Celery task (or async function) submit\_pod\_order\_task(order\_id).  
   * **Action (Backend \- Test First):** Write unit tests mocking the POD API client (httpx) and DB interactions:  
     * Test fetching required order/story/image data from DB (mocked).  
     * Test constructing the correct payload for the POD API based on their docs.  
     * Test successful API call: Verify mocked httpx.post is called correctly, POD Order ID is extracted from mocked response, Order status and pod\_order\_id are updated in DB (mocked).  
     * Test POD API error handling: Verify exceptions from mocked httpx are caught, logged, and order status reflects failure.  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the task logic: Fetch data, build payload, call POD API using httpx, process response, update DB. Add error handling/logging.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up task logic.  
   * **Action:** Commit (feat(backend): implement POD order submission task with TDD).  
6. **Task 2.15 (Continued): Finalize Order History Endpoints (TDD)**  
   * **Action (Backend \- Test First):** Update integration tests (TestClient) for GET /v1/orders and GET /v1/orders/{order\_id}:  
     * Test retrieving orders with various statuses (pending, paid, processing, failed). Verify response structure includes necessary details (status, date, amount, story link/info).  
   * **Action:** Run tests. **Verify they fail/pass.**  
   * **Action (Code):** Refine endpoint logic and queries to return relevant order history data.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up logic.  
   * **Action:** Commit (feat(backend): finalize order history endpoints with TDD).

**Phase 1 Continued: Frontend Development (Ref: Weeds 3.x)**

7. **Task 3.11 (Continued): Implement Real Photo Upload (TDD)**  
   * **Action (Frontend \- Test First):** Write integration tests (integration\_test package) or manual tests for the photo upload flow:  
     * Test selecting a file using image\_picker/file\_picker on target platforms (Web, iOS Simulator/Device).  
     * Test successfully getting the pre-signed URL from the (staging) backend.  
     * Test performing the actual HTTP PUT/POST request to the cloud storage URL using dio or http, sending the file data. Verify success/failure based on the response from cloud storage.  
     * Test updating UI state (progress, success preview, error message) based on the *actual* upload result.  
   * **Action:** Run tests (manual or integration). **Verify they fail/pass.**  
   * **Action (Code):** Replace the mocked upload logic from Sprint 2 (Task 9\) with the actual implementation:  
     1. Get pre-signed URL from backend.  
     2. Get file using image\_picker/file\_picker.  
     3. Use dio or http to send the file bytes to the pre-signed URL according to S3/GCS requirements (correct method, headers, body). Handle potential CORS issues if uploading directly from web.  
     4. Update UI based on the upload response. Store the photo identifier returned by the backend (or the generated key) in the wizard state.  
   * **Action:** Run tests again. **Verify they pass.**  
   * **Action (Refactor):** Clean up upload logic.  
   * **Action:** Commit (feat(frontend): implement real photo upload to cloud storage).  
8. **Task 3.13: Implement Story Preview Screen (TDD)**  
   * **Action (Frontend \- Test First):** Write widget tests (flutter\_test) for the Story Preview screen:  
     * Test initial loading state while fetching story data. Mock the API service call.  
     * Test error state display if fetching fails. Mock API service error.  
     * Test success state: Verify correct number of pages are displayed (PageView). Verify text and images (using placeholder/mocked image widgets initially) are shown for the current page based on mocked API data.  
     * Test page navigation updates the displayed content.  
     * Test presence of "Order Book" button.  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the Story Preview screen widget.  
     * On load, call the ApiClientService to fetch story data (GET /v1/stories/{story\_id}). Use the story ID obtained after generation (Task 3.12, Sprint 2).  
     * Manage loading/error/success states using the WizardStateNotifier/WizardBloc or a local state notifier.  
     * Use a PageView or similar widget to display pages.  
     * For each page, display the text segment and load the personalized image using its key/URL from the fetched data (use Image.network or a cached network image package). Handle image loading/error states.  
     * Implement navigation controls (or rely on PageView swipe).  
     * Add the "Order Book" button, navigating to the Checkout flow on tap.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up preview screen code.  
   * **Action:** Commit (feat(frontend): implement story preview screen with TDD).  
9. **Task 3.14: Implement Basic Checkout UI (Shipping & Payment Intent) (TDD)**  
   * **Action (Frontend \- Test First):** Write widget tests for the Shipping Address screen/form:  
     * Test UI elements render (TextFields for address fields).  
     * Test form validation (e.g., required fields).  
     * Test state updates on input.  
     * Test "Proceed to Payment" button calls a method on the state notifier/bloc to store address and navigate.  
   * **Action (Frontend \- Test First):** Write widget tests for the Payment screen:  
     * Test it calls the backend to create a Payment Intent (POST /v1/orders) on load (mock API service).  
     * Test display of loading state while creating intent.  
     * Test display of order summary (price).  
     * Test integration with chosen Stripe method (mock stripe\_flutter or UI elements calling backend).  
     * Test "Pay" button interaction triggers payment confirmation logic (mocked).  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the Shipping Address form widget and state logic. Implement the Payment screen widget:  
     * Call backend POST /v1/orders to create Payment Intent, passing story ID and shipping info. Store client secret received.  
     * Integrate Stripe: Use stripe\_flutter package with the client secret to display payment elements, OR build custom UI and call backend endpoint to confirm payment with Stripe details.  
     * Handle payment success/failure callbacks from Stripe, update state, navigate to Confirmation screen (Task 10\) or show error.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up checkout flow code.  
   * **Action:** Commit (feat(frontend): implement basic checkout UI flow with TDD).  
10. **Task 3.15: Implement Order Confirmation Screen (TDD)**  
    * **Action (Frontend \- Test First):** Write widget tests verifying the screen displays basic success message and order details (passed via navigation or fetched based on state). Test navigation options (e.g., back to home, view order history).  
    * **Action:** Run tests. **Verify they fail.**  
    * **Action (Code):** Implement the Order Confirmation screen widget.  
    * **Action:** Run tests. **Verify they pass.**  
    * **Action:** Commit (feat(frontend): implement order confirmation screen with TDD).  
11. **Task 3.16: Implement Order History Screen (TDD)**  
    * **Action (Frontend \- Test First):** Write widget tests:  
      * Test loading state while fetching orders. Mock API service.  
      * Test error state display. Mock API service error.  
      * Test success state displays a list (ListView) of orders with key details (Date, Status, Amount) based on mocked API data.  
    * **Action:** Run tests. **Verify they fail.**  
    * **Action (Code):** Implement the Order History screen widget. Fetch data from GET /v1/orders via ApiClientService. Manage state. Display data in a list.  
    * **Action:** Run tests. **Verify they pass.**  
    * **Action (Refactor):** Clean up screen code.  
    * **Action:** Commit (feat(frontend): implement order history screen with TDD).

**Next Steps (Sprint 4 Focus):**

* **Testing & QA:** Heavy focus on end-to-end testing of the full Wizard \-\> Generate \-\> Preview \-\> Order flow with *real* (staging) AI calls. Bug fixing.  
* **Ops:** Deploy Celery workers to staging. Refine monitoring & alerting, especially for AI costs and background task failures.  
* **Backend:** Implement remaining endpoints/logic (e.g., password reset, detailed order view, feedback mechanism). Refine error handling.  
* **Frontend:** UI Polish, implement remaining screens (e.g., account settings, feedback UI), refine responsive layouts, handle edge cases identified in testing.  
* **Security/Compliance:** Final checks, implement VPC if needed.

Sprint 3 is the big one – connecting all the major pieces. It'll likely uncover edge cases and require careful debugging, especially around the asynchronous AI tasks and the checkout flow. Keep communication tight between frontend and backend. You got this.