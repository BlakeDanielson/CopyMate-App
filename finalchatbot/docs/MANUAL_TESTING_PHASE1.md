# LLM Chat Application - Phase 1 Manual Testing

**Objective:** Manually verify the core functionality of the LLM Chat Application Phase 1 as defined in `docs/SPECIFICATION.md`.

**Phase 1 Goal:** Create a functional chat interface where a user can send a message and receive a response from an external LLM via a tRPC backend, without user accounts or message history persistence.

---

## 1. Prerequisites

*   The application backend and frontend must be running locally.
*   Environment variables (`LLM_API_KEY`, `LLM_API_ENDPOINT`) must be correctly configured in a `.env` file for the backend to communicate with the LLM service.
*   Open the application in your web browser (typically `http://localhost:3000`).

---

## 2. Test Cases

Perform the following tests sequentially. Record any deviations from the expected results.

### Test Case 1: Initial UI Load (FR1)

*   **Steps:**
    1.  Load the application URL in your browser.
*   **Expected Result:**
    *   The chat interface is displayed.
    *   A message input area (text box) is visible and empty.
    *   A "Send" button (or equivalent submission mechanism) is visible.
    *   The conversation display area is visible and initially empty (no messages).

### Test Case 2: Typing a Message (FR2)

*   **Steps:**
    1.  Click into the message input area.
    2.  Type a simple message (e.g., "Hello").
*   **Expected Result:**
    *   The text "Hello" appears in the input area as you type.

### Test Case 3: Sending a Message (FR3, FR4, FR8)

*   **Steps:**
    1.  Ensure there is text in the input area (e.g., "Hello").
    2.  Click the "Send" button or press Enter.
*   **Expected Result:**
    *   The message "Hello" appears in the conversation display area, marked as sent by the "user".
    *   The input area is cleared.
    *   (See Test Case 4 for the LLM response).

### Test Case 4: Receiving LLM Response (FR5, FR6, FR7, FR8)

*   **Steps:**
    1.  After sending the message in Test Case 3, wait for the response.
*   **Expected Result:**
    *   A response message from the LLM appears below the user's message in the conversation display area, marked as sent by the "llm".
    *   The content of the response should be relevant to the message sent (e.g., a greeting in response to "Hello").

### Test Case 5: Loading State (FR9)

*   **Steps:**
    1.  Send another message (e.g., "Tell me a short joke").
    2.  Observe the UI *while* waiting for the LLM response.
*   **Expected Result:**
    *   A visual indicator (e.g., a spinner, disabled input/button, text message) should appear, signifying that the application is waiting for the LLM response.
    *   This indicator should disappear once the response is received and displayed.

### Test Case 6: Empty Message Submission (Ref: FR3/Pseudocode)

*   **Steps:**
    1.  Ensure the message input area is completely empty.
    2.  Click the "Send" button or press Enter.
*   **Expected Result:**
    *   Nothing happens. No message is added to the conversation display, and no API call is made. The input area remains empty.

### Test Case 7: Multiple Messages (Session History - C2)

*   **Steps:**
    1.  Send several messages back and forth with the LLM.
    2.  Verify the conversation flow.
    3.  Reload the browser page (F5 or Cmd+R/Ctrl+R).
*   **Expected Result:**
    *   Each user message and corresponding LLM response should appear sequentially in the display area during the session.
    *   After reloading the page, the conversation display area should be empty again (confirming no persistence as per C2).

### Test Case 8: Basic Error Handling (FR10) - *Optional Setup*

*   **Goal:** Verify that the frontend displays an error if the backend fails to get a response from the LLM.
*   **Potential Setup (Requires backend modification or network simulation):**
    *   *Option A (Backend):* Temporarily stop the backend server and try sending a message.
    *   *Option B (Backend):* Temporarily modify the `.env` file with an invalid `LLM_API_KEY` or `LLM_API_ENDPOINT`, restart the backend, and try sending a message.
    *   *Option C (Network):* Use browser developer tools to simulate network failure for the API request when sending a message.
*   **Steps:**
    1.  If using Setup A, B, or C, trigger the error condition.
    2.  Send a message from the frontend.
*   **Expected Result:**
    *   The user's message might appear optimistically (depending on implementation).
    *   Instead of an LLM response, a clear error message (e.g., "Failed to get response. Please try again.") should be displayed in the UI.
    *   The loading indicator should disappear.
    *   *(Cleanup):* Remember to revert any changes made during setup (restart backend, fix `.env`, disable network simulation).

---

## 3. Reporting

*   Document any test case where the actual result differs from the expected result. Include steps to reproduce the issue.
*   Note any usability issues or unexpected behavior observed during testing.