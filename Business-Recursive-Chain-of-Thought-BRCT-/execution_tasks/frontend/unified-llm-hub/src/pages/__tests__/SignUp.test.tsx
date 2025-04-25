import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import SignUp from '../SignUp';
import { authService } from '../../services/api/auth.service';

// Mock the auth service and react-router's useNavigate
jest.mock('../../services/api/auth.service', () => ({
  authService: {
    signup: jest.fn(),
  },
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('SignUp Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderSignUp = () => {
    return render(
      <BrowserRouter>
        <SignUp />
      </BrowserRouter>
    );
  };

  it('should render all form fields and elements', () => {
    renderSignUp();
    
    // Check heading
    expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument();
    
    // Check form fields
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    
    // Check submit button
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
    
    // Check password visibility toggle buttons
    expect(screen.getAllByText(/show/i).length).toBe(2);
    
    // Check login link
    expect(screen.getByText(/already have an account\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /log in/i })).toBeInTheDocument();
  });

  it('should show validation errors for empty fields', async () => {
    renderSignUp();
    
    // Submit the form without filling any fields
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Check for validation error messages
    expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/confirm password is required/i)).toBeInTheDocument();
  });

  it('should validate email format', async () => {
    renderSignUp();
    
    // Enter invalid email and submit
    await userEvent.type(screen.getByLabelText(/email address/i), 'invalid-email');
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Check for validation error message
    expect(await screen.findByText(/please enter a valid email address/i)).toBeInTheDocument();
  });

  it('should validate password complexity', async () => {
    renderSignUp();
    
    // Enter a simple password and submit
    await userEvent.type(screen.getByLabelText(/^password$/i), 'simple');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'simple');
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Check for password complexity validation errors
    expect(await screen.findByText(/password must be at least 8 characters/i)).toBeInTheDocument();
  });

  it('should validate password match', async () => {
    renderSignUp();
    
    // Enter different passwords
    await userEvent.type(screen.getByLabelText(/^password$/i), 'StrongPassword123!');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'DifferentPassword123!');
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Check for password match error
    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
  });

  it('should toggle password visibility', async () => {
    renderSignUp();
    
    // Check initial state (password field is obscured)
    const passwordInput = screen.getByLabelText(/^password$/i);
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click show button to make password visible
    const showPasswordBtn = screen.getAllByText(/show/i)[0];
    fireEvent.click(showPasswordBtn);
    
    // Password should now be visible as text
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click hide button to obscure password again
    const hidePasswordBtn = screen.getByText(/hide/i);
    fireEvent.click(hidePasswordBtn);
    
    // Password should be obscured again
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('should submit the form and redirect to login page on successful signup', async () => {
    renderSignUp();
    
    // Mock the authService.signup to resolve successfully
    (authService.signup as jest.Mock).mockResolvedValueOnce(undefined);
    
    // Fill out the form correctly
    await userEvent.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'StrongPassword123!');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'StrongPassword123!');
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Wait for the submission to complete
    await waitFor(() => {
      // Check if the auth service was called with the right parameters
      expect(authService.signup).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'StrongPassword123!',
        confirmPassword: 'StrongPassword123!'
      });
      
      // Check navigation to login page
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  it('should display an error message when email already exists', async () => {
    renderSignUp();
    
    // Mock the authService.signup to reject with an 'already exists' error
    const emailExistsError = new Error('Email already exists');
    emailExistsError.response = {
      data: { message: 'Email already exists' }
    };
    (authService.signup as jest.Mock).mockRejectedValueOnce(emailExistsError);
    
    // Fill out the form
    await userEvent.type(screen.getByLabelText(/email address/i), 'existing@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'StrongPassword123!');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'StrongPassword123!');
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Check for the error message with login link
    await waitFor(() => {
      expect(screen.getByText(/an account with this email address already exists/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument();
    });
  });

  it('should display a generic error message on other API errors', async () => {
    renderSignUp();
    
    // Mock the authService.signup to reject with a generic error
    const serverError = new Error('Internal server error');
    serverError.response = {
      data: { message: 'Internal server error' }
    };
    (authService.signup as jest.Mock).mockRejectedValueOnce(serverError);
    
    // Fill out the form
    await userEvent.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'StrongPassword123!');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'StrongPassword123!');
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Check for the generic error message
    await waitFor(() => {
      expect(screen.getByText(/internal server error/i)).toBeInTheDocument();
    });
  });

  it('should disable the sign up button during form submission', async () => {
    renderSignUp();
    
    // Mock the authService.signup to take some time to resolve
    (authService.signup as jest.Mock).mockImplementationOnce(() => {
      return new Promise(resolve => {
        setTimeout(() => resolve(undefined), 100);
      });
    });
    
    // Fill out the form
    await userEvent.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'StrongPassword123!');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'StrongPassword123!');
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Check button is disabled and shows loading text
    expect(screen.getByRole('button', { name: /creating account/i })).toBeDisabled();
    
    // Wait for submission to complete
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });
});