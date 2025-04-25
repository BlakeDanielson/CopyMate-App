import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/api/auth.service'; // Import the auth service instance
import './SignUp.css';

const SignUp: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    let isValid = true;

    // Email validation
    if (!email) {
      newErrors.email = 'Email is required.';
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address.';
      isValid = false;
    }

    // Password validation
    if (!password) {
      newErrors.password = 'Password is required.';
      isValid = false;
    } else {
      if (password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters.';
        isValid = false;
      }
      if (!/[A-Z]/.test(password)) {
        newErrors.password = (newErrors.password ? newErrors.password + ' ' : '') + 'Requires uppercase.';
         isValid = false;
      }
       if (!/[a-z]/.test(password)) {
         newErrors.password = (newErrors.password ? newErrors.password + ' ' : '') + 'Requires lowercase.';
         isValid = false;
       }
       if (!/[0-9]/.test(password)) {
         newErrors.password = (newErrors.password ? newErrors.password + ' ' : '') + 'Requires number.';
         isValid = false;
       }
       if (!/[!@#$%^&*]/.test(password)) {
         newErrors.password = (newErrors.password ? newErrors.password + ' ' : '') + 'Requires special character (!@#$%^&*).';
         isValid = false;
       }
    }


    // Confirm Password validation
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Confirm Password is required.';
      isValid = false;
    } else if (password && confirmPassword !== password) {
      newErrors.confirmPassword = 'Passwords do not match.';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setApiError(null); // Clear previous API errors

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      // Call the actual signup API service function
      await authService.signup({ email, password, confirmPassword });

      // On successful signup, redirect to login page
      navigate('/login');

    } catch (error: any) {
      console.error('Signup failed:', error);
      // Handle API errors (e.g., email exists, server error)
      const message = error.response?.data?.message || error.message || 'An unexpected error occurred during sign-up. Please try again later.';
      // Display specific error for email conflict
      if (message.includes('Email already exists') || message.includes('already exists')) {
         setApiError('An account with this email address already exists. Please '); // Link added separately
      } else {
         setApiError(message);
      }
      setErrors({}); // Clear field-specific errors if API error occurs
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <h2>Create Account</h2>
      <form onSubmit={handleSubmit} noValidate>
        {apiError && (
          <p className="error-message api-error">
            {apiError}
            {apiError.includes('already exists') && <Link to="/login">login</Link>}
            {apiError.includes('already exists') && '.'}
          </p>
        )}

        <div className="form-group">
          <label htmlFor="email">Email Address</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? "email-error" : undefined}
          />
          {errors.email && <p id="email-error" className="error-message">{errors.email}</p>}
        </div>

        <div className="form-group password-group">
          <label htmlFor="password">Password</label>
          <input
            type={showPassword ? 'text' : 'password'}
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            aria-invalid={!!errors.password}
            aria-describedby={errors.password ? "password-error" : undefined}
          />
          <button
             type="button"
             onClick={() => setShowPassword(!showPassword)}
             className="password-toggle"
             aria-label={showPassword ? "Hide password" : "Show password"}
           >
             {showPassword ? 'Hide' : 'Show'}
           </button>
          {errors.password && <p id="password-error" className="error-message">{errors.password}</p>}
        </div>

         <div className="form-group password-group">
           <label htmlFor="confirmPassword">Confirm Password</label>
           <input
             type={showConfirmPassword ? 'text' : 'password'}
             id="confirmPassword"
             value={confirmPassword}
             onChange={(e) => setConfirmPassword(e.target.value)}
             required
             aria-invalid={!!errors.confirmPassword}
             aria-describedby={errors.confirmPassword ? "confirmPassword-error" : undefined}
           />
           <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="password-toggle"
              aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
            >
              {showConfirmPassword ? 'Hide' : 'Show'}
            </button>
           {errors.confirmPassword && <p id="confirmPassword-error" className="error-message">{errors.confirmPassword}</p>}
         </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>
      <p className="login-link">
        Already have an account? <Link to="/login">Log In</Link>
      </p>
    </div>
  );
};

export default SignUp;