# LLM Chat Application - Phase 1 Specification

**Project:** LLM Chat Application (Initial Phase)

**Technologies:** TypeScript, Next.js (App Router), tRPC, Tailwind CSS

**Phase 1 Goal:** Create a functional chat interface where a user can send a message and receive a response from an external LLM via a tRPC backend, without user accounts or message history persistence.

---

## 1. Functional Requirements (Phase 1)

*   **FR1:** Display a chat interface with a message input area and a display area for conversation history (session-only).
*   **FR2:** Allow users to type a message into the input area.
*   **FR3:** Allow users to submit the message (e.g., by pressing Enter or clicking a Send button).
*   **FR4:** On submission, send the user's message to the backend API.
*   **FR5:** The backend API shall forward the message to an external LLM service.
*   **FR6:** The backend API shall receive the response from the LLM service.
*   **FR7:** The backend API shall return the LLM's response to the frontend.
*   **FR8:** The frontend shall display the user's message and the LLM's response in the conversation display area.
*   **FR9:** Handle basic loading states (e.g., indicate when waiting for the LLM response).
*   **FR10:** Handle basic error states (e.g., display an error if the API call fails).

---

## 2. Constraints & Assumptions (Phase 1)

*   **C1:** No user authentication is required. All interactions are anonymous.
*   **C2:** Chat history is not persisted between sessions or page reloads. State is managed client-side only for the current session.
*   **C3:** The specific external LLM API endpoint and any necessary API keys will be configured via environment variables (not hardcoded).
*   **C4:** Basic UI styling will be handled by Tailwind CSS.
*   **C5:** Error handling will be basic (e.g., displaying a generic error message).

---

## 3. Module Specifications & Pseudocode

### 3.1. Frontend (`src/app/page.tsx`, `src/components/`)

*   **Responsibilities:**
    *   Render the main chat UI (`ChatInterface`).
    *   Manage local state for the current message input and the list of messages displayed.
    *   Utilize the tRPC client (`api.chat.sendMessage.useMutation`) to communicate with the backend.
    *   Update the UI based on API responses, loading states, and errors.

*   **`ChatInterface.tsx` (Conceptual Pseudocode)**

    ```typescript
    // TDD: Test rendering of ChatInput and MessageList components.
    // TDD: Test initial state (empty input, no messages).

    Component ChatInterface:
      STATE messages: Array<MessageObject> = [] // MessageObject: { id: string, sender: 'user' | 'llm', text: string }
      STATE currentInput: string = ""
      STATE isLoading: boolean = false
      STATE error: string | null = null

      // tRPC hook for sending messages
      // TDD: Test that useMutation is called correctly.
      // TDD: Test UI updates on mutation success (adds user message, adds LLM reply, clears input, sets isLoading false).
      // TDD: Test UI updates on mutation error (sets error state, sets isLoading false).
      // TDD: Test UI updates during mutation loading (sets isLoading true).
      sendMessageMutation = useTrpcMutation('chat.sendMessage', {
        onMutate: (variables) => {
          // Optional: Optimistic update
          setIsLoading(true);
          setError(null);
        },
        onSuccess: (data, variables) => {
          addMessage({ id: generateId(), sender: 'user', text: variables.message });
          addMessage({ id: generateId(), sender: 'llm', text: data.reply });
          setCurrentInput(""); // Clear input on success
        },
        onError: (error) => {
          setError("Failed to get response. Please try again.");
          // TDD: Test specific error message display.
        },
        onSettled: () => {
          setIsLoading(false);
        }
      });

      FUNCTION handleInputChange(event):
        setCurrentInput(event.target.value);
      END FUNCTION

      FUNCTION handleSubmit():
        trimmedInput = currentInput.trim();
        IF trimmedInput.length > 0 THEN
          // TDD: Test calling sendMessageMutation.mutate with correct input.
          sendMessageMutation.mutate({ message: trimmedInput });
        ELSE
          // TDD: Test that mutation is NOT called for empty input.
        END IF
      END FUNCTION

      FUNCTION addMessage(message: MessageObject):
        setMessages(previousMessages => [...previousMessages, message]);
      END FUNCTION

      RENDER:
        DIV container:
          MessageList(messages=messages) // Displays the array of messages
          // TDD: Test that MessageList receives the correct messages prop.
          IF error THEN
            DIV errorDisplay: error
            // TDD: Test conditional rendering of error message.
          END IF
          ChatInput(
            value=currentInput,
            onChange=handleInputChange,
            onSubmit=handleSubmit,
            isLoading=isLoading
          )
          // TDD: Test that ChatInput receives correct props and callbacks.
          // TDD: Test that isLoading state disables input/button in ChatInput.
        END DIV
      END RENDER
    End Component
    ```

*   **`ChatInput.tsx`, `MessageList.tsx`, `MessageItem.tsx`:** Standard presentational components receiving props.
    *   **TDD:** Test rendering based on props (value, messages, isLoading, etc.).
    *   **TDD:** Test callback invocation (onChange, onSubmit).

### 3.2. Backend - tRPC Router (`src/server/trpc/routers/chat.ts`)

*   **Responsibilities:** Define the `chat` router with procedures for chat functionality. Validate input, call appropriate services, format output.

*   **`chatRouter` Pseudocode:**

    ```typescript
    // Import necessary modules: trpc, zod, llmService
    // TDD: Test router definition and procedure existence.

    DEFINE chatRouter = createTRPCRouter({
      // --- sendMessage Procedure ---
      sendMessage: publicProcedure
        // Input Validation
        // TDD: Test input validation (requires message string, min length 1).
        // TDD: Test failure case for empty/missing message.
        .input(z.object({ message: z.string().min(1) }))
        // Output Definition
        // TDD: Test output shape (object with 'reply' string).
        .output(z.object({ reply: z.string() }))
        // Mutation Logic
        .mutation(ASYNC ({ input }) => {
          TRY
            // TDD: Test that llmService.getCompletion is called with input.message.
            // TDD: Test successful return path (returns { reply: ... }).
            llmReply = AWAIT llmService.getCompletion(input.message);
            RETURN { reply: llmReply };
          CATCH error
            // TDD: Test error handling (throws TRPCError on llmService failure).
            logError("LLM Service failed", error);
            THROW new TRPCError({
              code: 'INTERNAL_SERVER_ERROR',
              message: 'Failed to communicate with the LLM service.',
            });
          END TRY
        }) // End mutation
    }); // End chatRouter
    ```

### 3.3. Backend - LLM Service (`src/server/services/llmService.ts`)

*   **Responsibilities:** Abstract the interaction with the external LLM API. Handle request formatting, API calls, and response parsing. Read configuration (API key, endpoint) from environment variables.

*   **`llmService` Pseudocode:**

    ```typescript
    // TDD: Test service instantiation (reading config from env vars).
    // TDD: Test failure if required env vars are missing.

    CLASS LLMService:
      PRIVATE apiKey: string
      PRIVATE apiEndpoint: string

      CONSTRUCTOR():
        apiKey = process.env.LLM_API_KEY;
        apiEndpoint = process.env.LLM_API_ENDPOINT;

        IF NOT apiKey OR NOT apiEndpoint THEN
          // TDD: Test this specific error condition.
          THROW new Error("Missing LLM API Key or Endpoint in environment variables.");
        END IF
      END CONSTRUCTOR

      // --- getCompletion Method ---
      PUBLIC ASYNC getCompletion(prompt: string): string
        // TDD: Test successful API call simulation (mock fetch/axios).
        // TDD: Test correct request formatting (headers, body, prompt).
        // TDD: Test successful response parsing.
        // TDD: Test handling of API error responses (e.g., 4xx, 5xx status codes).
        // TDD: Test handling of network errors during the API call.

        requestBody = { prompt: prompt, /* other LLM params */ };
        requestOptions = {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        };

        TRY
          response = AWAIT fetch(this.apiEndpoint, requestOptions);

          IF NOT response.ok THEN
            // TDD: Test specific error for non-ok response.
            errorBody = AWAIT response.text();
            logError(`LLM API Error: ${response.status}`, errorBody);
            THROW new Error(`LLM API request failed with status ${response.status}`);
          END IF

          responseData = AWAIT response.json();

          // Extract the actual text reply based on the specific LLM API structure
          // TDD: Test extraction logic for different valid response structures.
          replyText = responseData.choices[0].text; // Example structure

          IF typeof replyText !== 'string' THEN
             // TDD: Test error handling for unexpected response structure.
             logError("Unexpected LLM API response structure", responseData);
             THROW new Error("Invalid response format from LLM API.");
          END IF

          RETURN replyText;

        CATCH networkError
          // TDD: Test specific error for network issues.
          logError("Network error calling LLM API", networkError);
          THROW new Error("Failed to connect to the LLM service.");
        END CATCH
      END METHOD
    END CLASS

    // Export an instance
    EXPORT CONSTANT llmService = new LLMService();
    ```

---

## 4. Environment Variables (`.env.example`)

```env
# .env.example
# Configuration for the external LLM API
LLM_API_KEY="YOUR_LLM_API_KEY_HERE"
LLM_API_ENDPOINT="YOUR_LLM_API_ENDPOINT_HERE"

# NEXT_PUBLIC_ variables are exposed to the browser, avoid secrets here.
```

---

## 5. Next Steps & TDD Flow

1.  **Setup:** Initialize Next.js project, install dependencies (tRPC, Zod, Tailwind).
2.  **Backend Tests First:**
    *   Write tests for `LLMService` (mocking `fetch`/HTTP calls and environment variables).
    *   Write tests for `chatRouter.sendMessage` (mocking `llmService`).
3.  **Backend Implementation:** Implement `LLMService` and `chatRouter` to pass the tests.
4.  **Frontend Tests:**
    *   Write tests for individual UI components (`ChatInput`, `MessageList`, etc.).
    *   Write tests for `ChatInterface`, mocking the tRPC client hook (`useTrpcMutation`).
5.  **Frontend Implementation:** Implement the React components and integrate the tRPC client.
6.  **Manual Testing:** Run the application and perform manual tests.