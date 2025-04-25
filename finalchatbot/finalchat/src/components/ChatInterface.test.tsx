import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatInterface } from './ChatInterface';
import { ChatInput } from './ChatInput';
import { MessageList } from './MessageList';

// Mock the tRPC hook
jest.mock('@trpc/react-query', () => ({
  createTRPCReact: jest.fn().mockReturnValue({
    chat: {
      sendMessage: {
        useMutation: jest.fn()
      }
    }
  })
}));

// Mock the child components
jest.mock('./ChatInput', () => ({
  ChatInput: jest.fn().mockImplementation(({ value, onChange, onSubmit, isLoading }) => (
    <div data-testid="chat-input-mock">
      <input 
        data-testid="input-field" 
        value={value} 
        onChange={onChange} 
        disabled={isLoading} 
      />
      <button 
        data-testid="submit-button" 
        onClick={onSubmit} 
        disabled={isLoading}
      >
        Send
      </button>
    </div>
  ))
}));

jest.mock('./MessageList', () => ({
  MessageList: jest.fn().mockImplementation(({ messages }) => (
    <div data-testid="message-list-mock">
      {messages.map(msg => (
        <div key={msg.id} data-testid="message-item" data-sender={msg.sender}>
          {msg.text}
        </div>
      ))}
    </div>
  ))
}));

// Helper function to get the mock tRPC mutation hook
const getMockMutationHook = (options = {}) => {
  const mockMutate = jest.fn();
  const mockHook = {
    mutate: mockMutate,
    isLoading: false,
    isError: false,
    error: null,
    ...options
  };
  
  // This accesses the mock function created in the jest.mock call above
  const useMutationMock = require('@trpc/react-query').createTRPCReact().chat.sendMessage.useMutation;
  useMutationMock.mockReturnValue(mockHook);
  
  return { useMutationMock, mockMutate };
};

describe('ChatInterface Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders ChatInput and MessageList components', () => {
    const { mockMutate } = getMockMutationHook();
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: () => ({
            mutate: mockMutate,
            isPending: false
          })
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    expect(screen.getByTestId('chat-input-mock')).toBeInTheDocument();
    expect(screen.getByTestId('message-list-mock')).toBeInTheDocument();
    expect(ChatInput).toHaveBeenCalledTimes(1);
    expect(MessageList).toHaveBeenCalledTimes(1);
  });

  test('initializes with empty input and no messages', () => {
    const { mockMutate } = getMockMutationHook();
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: () => ({
            mutate: mockMutate,
            isPending: false
          })
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    // Get the first call arguments to ChatInput
    const chatInputProps = ChatInput.mock.calls[0][0];
    
    // Verify the props
    expect(chatInputProps.value).toBe('');
    expect(chatInputProps.isLoading).toBe(false);
    
    // Get the first call arguments to MessageList
    const messageListProps = MessageList.mock.calls[0][0];
    
    // Verify the props
    expect(messageListProps.messages).toEqual([]);
  });

  test('updates input value when typing', async () => {
    const { mockMutate } = getMockMutationHook();
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: () => ({
            mutate: mockMutate,
            isPending: false
          })
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    const inputField = screen.getByTestId('input-field');
    
    // Wrap state update in act
    await act(async () => {
      fireEvent.change(inputField, { target: { value: 'Hello world' } });
    });
    
    // Get the latest call to ChatInput
    const lastCallIndex = ChatInput.mock.calls.length - 1;
    const chatInputProps = ChatInput.mock.calls[lastCallIndex][0];
    
    // Verify the input value was updated
    expect(chatInputProps.value).toBe('Hello world');
  });

  test('calls mutation with correct input when submitting a message', async () => {
    const { mockMutate } = getMockMutationHook();
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: () => ({
            mutate: mockMutate,
            isPending: false
          })
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    // Type a message
    const inputField = screen.getByTestId('input-field');
    await act(async () => {
      fireEvent.change(inputField, { target: { value: 'Test message' } });
    });
    
    // Submit the message
    const submitButton = screen.getByTestId('submit-button');
    await act(async () => {
      fireEvent.click(submitButton);
    });
    
    // Verify the mutation was called with the correct input
    expect(mockMutate).toHaveBeenCalledWith({ message: 'Test message' });
  });

  test('does not call mutation when submitting empty message', async () => {
    const { mockMutate } = getMockMutationHook();
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: () => ({
            mutate: mockMutate,
            isPending: false
          })
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    // Submit without typing anything
    const submitButton = screen.getByTestId('submit-button');
    await act(async () => {
      fireEvent.click(submitButton);
    });
    
    // Verify the mutation was not called
    expect(mockMutate).not.toHaveBeenCalled();
  });

  test('updates isLoading state when mutation starts and completes', async () => {
    // Setup the mutation hook
    const { mockMutate } = getMockMutationHook();
    let savedConfig;
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: (config) => {
            // Store the callbacks for later use in the test
            savedConfig = config;
            return {
              mutate: mockMutate,
              isPending: false
            };
          }
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    // Get the callbacks from our saved config
    const onMutate = savedConfig.onMutate;
    const onSettled = savedConfig.onSettled;
    
    // Initially, ChatInput should not be in loading state
    const initialChatInputProps = ChatInput.mock.calls[0][0];
    expect(initialChatInputProps.isLoading).toBe(false);
    
    // Simulate mutation starting
    await act(async () => {
      onMutate({ message: 'Test message' });
    });
    
    // After onMutate, ChatInput should be in loading state
    await waitFor(() => {
      // Get latest props after state update
      const latestIndex = ChatInput.mock.calls.length - 1;
      const loadingChatInputProps = ChatInput.mock.calls[latestIndex][0];
      expect(loadingChatInputProps.isLoading).toBe(true);
    });
    
    // Simulate mutation completing
    await act(async () => {
      onSettled();
    });
    
    // After onSettled, ChatInput should not be in loading state
    await waitFor(() => {
      // Get latest props after state update
      const finalIndex = ChatInput.mock.calls.length - 1;
      const finalChatInputProps = ChatInput.mock.calls[finalIndex][0];
      expect(finalChatInputProps.isLoading).toBe(false);
    });
  });

  test('adds messages to the list on successful mutation', async () => {
    // Set up the mutation hook
    const { mockMutate } = getMockMutationHook();
    let savedConfig;
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: (config) => {
            savedConfig = config;
            return {
              mutate: mockMutate,
              isPending: false
            };
          }
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    // Type and submit a message
    const inputField = screen.getByTestId('input-field');
    await act(async () => {
      fireEvent.change(inputField, { target: { value: 'Hello LLM' } });
    });
    
    const submitButton = screen.getByTestId('submit-button');
    await act(async () => {
      fireEvent.click(submitButton);
    });
    
    // Prepare data for onSuccess
    const userMessage = 'Hello LLM';
    const llmResponse = 'Hello, I am an LLM assistant';
    
    // First, call onMutate to add the user message
    await act(async () => {
      savedConfig.onMutate({ message: userMessage });
    });
    
    // Then call onSuccess to add the LLM response
    await act(async () => {
      savedConfig.onSuccess({ reply: llmResponse }, { message: userMessage });
    });
    
    // Check MessageList props
    await waitFor(() => {
      // Get the last call to MessageList
      const lastCallIndex = MessageList.mock.calls.length - 1;
      const messageListProps = MessageList.mock.calls[lastCallIndex][0];
      
      // Check that the messages array has both messages
      expect(messageListProps.messages.length).toBe(2);
      expect(messageListProps.messages[0].sender).toBe('user');
      expect(messageListProps.messages[0].text).toBe(userMessage);
      expect(messageListProps.messages[1].sender).toBe('llm');
      expect(messageListProps.messages[1].text).toBe(llmResponse);
    });
    
    // Input should be cleared
    await waitFor(() => {
      // Get the last call to ChatInput
      const lastCallIndex = ChatInput.mock.calls.length - 1;
      const chatInputProps = ChatInput.mock.calls[lastCallIndex][0];
      
      expect(chatInputProps.value).toBe('');
    });
  });

  test('displays error message when mutation fails', async () => {
    // Set up the mutation hook
    const { mockMutate } = getMockMutationHook();
    let savedConfig;
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: (config) => {
            savedConfig = config;
            return {
              mutate: mockMutate,
              isPending: false
            };
          }
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    // Get the onError callback from our saved config
    const onError = savedConfig.onError;
    
    // Wrap the callback in act
    await act(async () => {
      // Call the onError handler with an error
      onError(new Error('API error'));
    });
    
    // Error message should be displayed
    await waitFor(() => {
      expect(screen.getByText(/Error: API error/i)).toBeInTheDocument();
    });
  });

  test('clears error message when starting a new mutation', async () => {
    // Set up the mutation hook
    const { mockMutate } = getMockMutationHook();
    let savedConfig;
    
    // Create mock API for the component
    const mockApi = {
      chat: {
        sendMessage: {
          useMutation: (config) => {
            savedConfig = config;
            return {
              mutate: mockMutate,
              isPending: false
            };
          }
        }
      }
    };
    
    render(<ChatInterface api={mockApi} />);
    
    // First, set an error - use our saved config
    const onError = savedConfig.onError;
    
    // Set error state
    await act(async () => {
      onError(new Error('API error'));
    });
    
    // Verify error is shown
    expect(screen.getByText(/Error: API error/i)).toBeInTheDocument();
    
    // Now, simulate starting a new mutation
    const onMutate = savedConfig.onMutate;
    
    // Call onMutate to clear error
    await act(async () => {
      onMutate({ message: 'New message' });
    });
    
    // Error should be cleared
    await waitFor(() => {
      expect(screen.queryByText(/Error: API error/i)).not.toBeInTheDocument();
    });
  });
});