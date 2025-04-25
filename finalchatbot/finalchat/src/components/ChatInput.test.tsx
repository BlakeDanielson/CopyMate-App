import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatInput } from './ChatInput';

describe('ChatInput Component', () => {
  const mockOnChange = jest.fn();
  const mockOnSubmit = jest.fn();
  
  beforeEach(() => {
    mockOnChange.mockClear();
    mockOnSubmit.mockClear();
  });

  test('renders input field and submit button', () => {
    render(
      <ChatInput 
        value="" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        isLoading={false} 
      />
    );
    
    expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  test('displays the current input value', () => {
    const testValue = 'Hello, world!';
    
    render(
      <ChatInput 
        value={testValue} 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        isLoading={false} 
      />
    );
    
    expect(screen.getByPlaceholderText(/type a message/i)).toHaveValue(testValue);
  });

  test('calls onChange handler when typing in input', () => {
    render(
      <ChatInput 
        value="" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        isLoading={false} 
      />
    );
    
    const input = screen.getByPlaceholderText(/type a message/i);
    fireEvent.change(input, { target: { value: 'New message' } });
    
    expect(mockOnChange).toHaveBeenCalledTimes(1);
  });

  test('calls onSubmit handler when clicking send button', () => {
    render(
      <ChatInput 
        value="Test message" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        isLoading={false} 
      />
    );
    
    const button = screen.getByRole('button', { name: /send/i });
    fireEvent.click(button);
    
    expect(mockOnSubmit).toHaveBeenCalledTimes(1);
  });

  test('calls onSubmit handler when pressing Enter in input field', () => {
    render(
      <ChatInput 
        value="Test message" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        isLoading={false} 
      />
    );
    
    const input = screen.getByPlaceholderText(/type a message/i);
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });
    
    expect(mockOnSubmit).toHaveBeenCalledTimes(1);
  });

  test('disables input and button when in loading state', () => {
    render(
      <ChatInput 
        value="Test message" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        isLoading={true} 
      />
    );
    
    const input = screen.getByPlaceholderText(/type a message/i);
    const button = screen.getByRole('button', { name: /send/i });
    
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });
});