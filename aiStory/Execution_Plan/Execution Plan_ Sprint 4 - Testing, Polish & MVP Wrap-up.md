# **Execution Plan: Sprint 4 \- Testing, Polish & MVP Wrap-up**

**Goal:** Achieve MVP release readiness through rigorous end-to-end testing (with live AI integrations), bug fixing, UI/UX polish, implementation of remaining essential MVP features (password reset, feedback), operational setup refinement, and final compliance checks.

**Reference:** tech\_spec\_v1 (Latest Version); execution\_plan\_sprint3\_v1 (Previous Sprint)

**Phase 1 Continued: Testing & QA Focus (Ref: Weeds 3.9)**

1. **Task 9.1 (Continued): Define & Execute E2E Test Scenarios**  
   * **Action (QA/Dev):** Define detailed E2E test cases covering the full user journey: Signup \-\> Wizard (various inputs) \-\> **Real AI Generation** \-\> Preview \-\> Checkout (Test Stripe) \-\> Order History verification \-\> Logout. Include edge cases (AI failures, invalid inputs, network interruptions). Document in Notion/Test Management Tool.  
   * **Action (QA/Dev):** Execute Flutter integration\_test suite against the **staging environment** (connected to real, sandboxed AI/Stripe/POD APIs). Automate as much as possible.  
   * **Action (QA):** Perform manual execution of the defined E2E test cases on primary target platforms (iPad/Web). Record results meticulously.  
2. **Task (New): Dedicated Bug Fixing**  
   * **Action (All Devs):** Prioritize and fix bugs identified during Sprint 3 and ongoing Sprint 4 E2E/QA testing based on severity. Link commits/PRs back to bug reports in Notion.  
   * **Action (QA):** Verify bug fixes on the staging environment.

**Phase 1 Continued: Ops Focus (Ref: Weeds 3.8)**

3. **Task 8.2 / 8.3 (Continued): Deploy Background Workers & Refine CI/CD**  
   * **Action (Ops):** Deploy the Celery worker service (from Task 1, Sprint 3\) alongside the API service to the **staging environment**. Ensure it connects to Redis and the DB.  
   * **Action (Ops):** Monitor worker logs in staging for successful task execution and errors related to AI calls.  
   * **Action (Ops):** Refine CI/CD pipelines: Ensure test reports are generated/archived. Stabilize build/deployment processes. Set up mechanism for production deployment (e.g., manual trigger from main branch build after QA sign-off).  
4. **Task (New): Monitoring & Alerting Refinement**  
   * **Action (Ops):** Implement/refine monitoring dashboards (using cloud provider tools, Grafana, etc.) to track key metrics identified in Tech Spec (API/AI latency/errors, DB performance, Celery queue length/task failures).  
   * **Action (Ops):** Configure critical alerts defined in Tech Spec (e.g., high 5xx rate, high AI failure rate, Celery queue backing up) targeting Slack/PagerDuty/Email.  
   * **Action (Ops):** Verify AI cost tracking mechanisms are functional and providing useful data from staging environment usage.

**Phase 1 Continued: Backend Development (Remaining MVP \- TDD) (Ref: Weeds 2.x)**

5. **Task (New): Implement Password Reset Flow (TDD)**  
   * **Action (Backend):** Define DB storage for reset tokens (e.g., separate table or column on users with expiry). Define relevant Pydantic schemas. Define API endpoints (POST /v1/auth/forgot-password, POST /v1/auth/reset-password).  
   * **Action (Backend \- Test First):** Write tests for:  
     * Forgot password endpoint: Validates email exists, generates secure token, stores token/expiry (mocked DB), triggers email sending task (mocked Celery/email client).  
     * Reset password endpoint: Validates token (exists, not expired \- mock DB), validates new password complexity, updates user's hashed password (mocked DB), invalidates reset token (mocked DB).  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the logic, including secure token generation, email sending task dispatch, token validation, and password update.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up code.  
   * **Action:** Add/Apply necessary Alembic migration.  
   * **Action:** Commit (feat(backend): implement password reset flow with TDD).  
6. **Task 2.13 (Refined): Implement Feedback Mechanism Endpoint (TDD)**  
   * **Action (Backend):** Define endpoint (POST /v1/stories/{story\_id}/feedback or similar). Define request schema (e.g., { "is\_appropriate": true/false, "comment": "Optional text" }). Define DB storage for feedback (e.g., link to stories or analysis\_results).  
   * **Action (Backend \- Test First):** Write integration tests (TestClient): Test endpoint requires auth, validates payload, stores feedback in DB (mocked).  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the endpoint and DB storage logic.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up code.  
   * **Action:** Add/Apply necessary Alembic migration.  
   * **Action:** Commit (feat(backend): implement story feedback endpoint with TDD).  
7. **Task 2.15 (Refined): Implement Detailed Order View Endpoint (TDD)**  
   * **Action (Backend):** Refine GET /v1/orders/{order\_id} endpoint. Ensure it joins necessary data (e.g., basic story info, shipping address) for a detailed view. Define response schema.  
   * **Action (Backend \- Test First):** Update integration tests (TestClient) to verify the refined response structure includes all necessary fields for the frontend detail view. Test access control (user can only view their own orders).  
   * **Action:** Run tests. **Verify they fail/pass.**  
   * **Action (Code):** Implement the necessary SQLAlchemy query refinements (joins) and update the Pydantic response model.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up query/endpoint logic.  
   * **Action:** Commit (feat(backend): refine order detail retrieval endpoint with TDD).  
8. **Task (New): Refine Global Error Handling**  
   * **Action (Backend):** Implement FastAPI Exception Handlers for common custom exceptions (e.g., AuthenticationError, NotFoundError, AIError) and potentially override default handlers (e.g., RequestValidationError) to return consistent JSON error structures defined earlier. Ensure sensitive details aren't leaked in production errors.  
   * **Action (Backend \- Test First):** Write/update integration tests to verify that specific error scenarios trigger the correct exception handler and return the expected standardized JSON error response and status code.  
   * **Action:** Run tests. **Verify they fail/pass.**  
   * **Action (Code):** Implement/refine exception handlers in FastAPI.  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action:** Commit (refactor(backend): implement standardized global error handling).

**Phase 1 Continued: Frontend Development (Polish & Remaining MVP \- TDD) (Ref: Weeds 3.x)**

9. **Task (New): Implement Account Settings Screen (TDD)**  
   * **Action (Frontend \- Test First):** Write widget tests for an Account Settings screen:  
     * Test UI elements (e.g., "Change Password" button, "Delete Account" button with confirmation).  
     * Test interactions trigger calls to mocked AuthNotifier/AuthBloc or API service methods.  
     * Test confirmation dialog logic for destructive actions (delete account).  
   * **Action:** Run tests. **Verify they fail.**  
   * **Action (Code):** Implement the Account Settings screen UI. Connect buttons to relevant backend API calls (e.g., initiate password change flow \- might navigate to a separate screen, trigger delete account endpoint).  
   * **Action:** Run tests. **Verify they pass.**  
   * **Action (Refactor):** Clean up screen code.  
   * **Action:** Commit (feat(frontend): implement basic account settings screen with TDD).  
   * **Note:** Full password change UI flow might span into next sprint depending on complexity.  
10. **Task (New): Implement Feedback UI**  
    * **Action (Frontend \- Test First):** Write widget tests for the UI element allowing feedback (e.g., a button/dialog on the Story Preview screen):  
      * Test interaction triggers call to mocked API service (POST /v1/stories/{story\_id}/feedback).  
      * Test UI updates on successful submission (e.g., confirmation message).  
    * **Action:** Run tests. **Verify they fail.**  
    * **Action (Code):** Implement the feedback UI element(s) and connect them to the backend API endpoint via the ApiClientService.  
    * **Action:** Run tests. **Verify they pass.**  
    * **Action (Refactor):** Clean up feedback UI code.  
    * **Action:** Commit (feat(frontend): implement story feedback UI with TDD).  
11. **Task (New): UI Polish & Responsiveness Pass**  
    * **Action (FE Dev/UI/UX):** Review all existing screens (Auth, Wizard, Preview, Checkout, Orders, Settings) on target platforms (iPad/Web primarily).  
    * **Action:** Identify and fix minor UI inconsistencies, spacing issues, typography errors, awkward responsive behavior. Use LayoutBuilder/MediaQuery as needed.  
    * **Action:** Ensure loading states and error messages are consistent and user-friendly across the app.  
    * **Action:** Commit polish fixes (fix(frontend): UI polish and responsiveness improvements). *Testing for this is primarily regression (ensure existing tests pass) and manual QA.*  
12. **Task (New): Handle Edge Cases & Errors**  
    * **Action (FE Dev):** Based on testing (Sprint 3 & 4), implement more robust handling for specific error conditions:  
      * Display clearer messages for specific AI generation failures (if backend provides codes/details).  
      * Handle network connectivity errors gracefully during API calls (dio error types).  
      * Improve handling of expired JWT tokens (trigger logout/refresh flow).  
    * **Action (Test First where applicable):** Write unit/widget tests for specific error handling logic in state notifiers/blocs or UI display logic.  
    * **Action:** Implement refinements.  
    * **Action:** Commit (fix(frontend): improve handling of specific error states and edge cases).

**Phase 1 Continued: Security & Compliance (Ref: Weeds 3.7)**

13. **Task 7.4 / 7.9: Implement VPC & Final Compliance Review**  
    * **Action (FE/BE/Legal):** If targeting users \<13, implement the chosen Verifiable Parental Consent (VPC) mechanism. This likely involves frontend UI changes and backend logic/verification steps. *Requires prior research and legal consultation.*  
    * **Action (Lead/Legal):** Conduct final review of implemented consent flows, privacy policy, and overall application against COPPA, GDPR, YouTube ToS, Google API Policy, and relevant local laws (e.g., Arizona). Document compliance status.  
14. **Task 9.3 (Continued): Final Security Review**  
    * **Action (Security Champion/QA/Dev):** Execute final security checklist (OWASP Top 10 basics, dependency scan (pip-audit, flutter pub outdated), review access controls, check for leaked secrets). Document findings. Address critical/high severity issues.

**Next Steps (Post-Sprint 4 / MVP Launch Prep):**

* **Go/No-Go Decision:** Based on Sprint 4 testing, bug status, compliance checks, and stakeholder review.  
* **Production Deployment:** Prepare production environment, run final deployment dry-run, execute production launch plan.  
* **Post-Launch Monitoring:** Closely monitor performance, errors, costs, and user feedback.  
* **Plan Phase 2:** Prioritize features based on MVP feedback and business goals.

This sprint is about hardening what you've built. Lots of testing, fixing, and adding those last crucial bits like password reset. Stay focused, crush those bugs, and get ready to ship that MVP.