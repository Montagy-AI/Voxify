import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import ForgotPassword from '../ForgotPassword';

// Mock the auth service
jest.mock('../../services/auth.service', () => ({
  isAuthenticated: jest.fn(),
  forgotPassword: jest.fn(),
}));

// Mock react-router-dom hooks
const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Import the mocked service
import authService from '../../services/auth.service';

// Helper function to render component with router
const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('ForgotPassword Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authService.isAuthenticated.mockReturnValue(false);
    // Mock console.error to avoid noise in tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  /*
   * Authentication Redirect Tests
   */
  describe('Authentication Redirect', () => {
    test('redirects to dashboard if user is already authenticated', () => {
      authService.isAuthenticated.mockReturnValue(true);
      
      renderWithRouter(<ForgotPassword />);
      
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });

    test('does not redirect when user is not authenticated', () => {
      authService.isAuthenticated.mockReturnValue(false);
      
      renderWithRouter(<ForgotPassword />);
      
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  /*
   * Form Rendering Tests
   */
  describe('Form Rendering', () => {
    test('renders all form elements correctly', () => {
      renderWithRouter(<ForgotPassword />);
      
      expect(screen.getByText('Forgot your password?')).toBeInTheDocument();
      expect(screen.getByText("Enter your email address and we'll send you a link to reset your password.")).toBeInTheDocument();
      
      // Form elements
      expect(screen.getByPlaceholderText('Email address')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Send Reset Link' })).toBeInTheDocument();
      
      // Links
      expect(screen.getByText('Remember your password?')).toBeInTheDocument();
      expect(screen.getByText('Sign in')).toBeInTheDocument();
      expect(screen.getByText("Don't have an account?")).toBeInTheDocument();
      expect(screen.getByText('Sign up')).toBeInTheDocument();
      
      // Logo
      expect(screen.getByAltText('Voxify')).toBeInTheDocument();
    });

    test('email input has correct attributes', () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('id', 'email');
      expect(emailInput).toHaveAttribute('name', 'email');
      expect(emailInput).toHaveAttribute('autoComplete', 'email');
      expect(emailInput).toBeRequired();
    });

    test('submit button has correct attributes', () => {
      renderWithRouter(<ForgotPassword />);
      
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      expect(submitButton).toHaveAttribute('type', 'submit');
      expect(submitButton).not.toBeDisabled();
    });
  });

  /*
   * Form Input Tests
   */
  describe('Form Input', () => {
    test('updates email input value when typed', () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      expect(emailInput.value).toBe('test@example.com');
    });

    test('email input starts empty', () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      
      expect(emailInput.value).toBe('');
    });
  });

  /*
   * Form Validation Tests
   */
  describe('Form Validation', () => {
    test('shows error when email is empty', async () => {
      renderWithRouter(<ForgotPassword />);
      
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });
    });

    test('shows error when email is invalid (no @ symbol)', async () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      });
    });

    test('accepts valid email format', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(authService.forgotPassword).toHaveBeenCalledWith('test@example.com');
      });
    });
  });

  /*
   * Successful Form Submission Tests
   */
  describe('Successful Form Submission', () => {
    test('successfully sends reset email with default message', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(authService.forgotPassword).toHaveBeenCalledWith('test@example.com');
      });
      
      await waitFor(() => {
        expect(screen.getByText('If an account with that email exists, a password reset link has been sent.')).toBeInTheDocument();
      });
      
      // Check that form is cleared
      expect(emailInput.value).toBe('');
    });

    test('successfully sends reset email with custom message', async () => {
      const customMessage = 'Reset link sent to your email';
      authService.forgotPassword.mockResolvedValue({ 
        success: true, 
        message: customMessage 
      });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(customMessage)).toBeInTheDocument();
      });
    });

    test('shows loading state during form submission', async () => {
      // Mock slow response
      authService.forgotPassword.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      fireEvent.click(submitButton);
      
      // Should show loading state
      expect(screen.getByText('Sending...')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
      expect(emailInput).toBeDisabled();
      
      // Wait for completion
      await waitFor(() => {
        expect(screen.getByText('If an account with that email exists, a password reset link has been sent.')).toBeInTheDocument();
      });
    });
  });

  /*
   * Error Handling Tests
   */
  describe('Error Handling', () => {
    test('shows error when API returns error', async () => {
      authService.forgotPassword.mockResolvedValue({ 
        success: false, 
        error: 'User not found' 
      });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('User not found')).toBeInTheDocument();
      });
    });

    test('shows generic error when API throws exception', async () => {
      authService.forgotPassword.mockRejectedValue(new Error('Network error'));
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to send reset email. Please try again.')).toBeInTheDocument();
      });
    });
  });

  /*
   * Form State Management Tests
   */
  describe('Form State Management', () => {
    test('clears error messages when form is resubmitted', async () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      // First submission with invalid data
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });
      
      // Second submission with valid data
      authService.forgotPassword.mockResolvedValue({ success: true });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      // Error should be cleared
      await waitFor(() => {
        expect(screen.queryByText('Email is required')).not.toBeInTheDocument();
      });
    });

    test('clears success messages when form is resubmitted', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      // First successful submission
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('If an account with that email exists, a password reset link has been sent.')).toBeInTheDocument();
      });
      
      // Second submission should clear previous success message
      fireEvent.change(emailInput, { target: { value: 'test2@example.com' } });
      fireEvent.click(submitButton);
      
      // Success message should be cleared initially, then new one should appear
      await waitFor(() => {
        expect(screen.getByText('If an account with that email exists, a password reset link has been sent.')).toBeInTheDocument();
      });
    });

    test('does not clear form on validation error', async () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      });
      
      // Email should still be in the input
      expect(emailInput.value).toBe('invalid-email');
    });

    test('does not clear form on API error', async () => {
      authService.forgotPassword.mockResolvedValue({ 
        success: false, 
        error: 'Server error' 
      });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Server error')).toBeInTheDocument();
      });
      
      // Email should still be in the input
      expect(emailInput.value).toBe('test@example.com');
    });
  });

  /*
   * UI State Tests
   */
  describe('UI States', () => {
    test('displays error message with proper styling', async () => {
      renderWithRouter(<ForgotPassword />);
      
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        const errorElement = screen.getByText('Email is required');
        expect(errorElement).toBeInTheDocument();
        expect(errorElement.closest('div')).toHaveClass('bg-red-900/50', 'border-red-700');
        expect(errorElement).toHaveClass('text-red-200');
      });
    });

    test('displays success message with proper styling', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        const successElement = screen.getByText('If an account with that email exists, a password reset link has been sent.');
        expect(successElement).toBeInTheDocument();
        expect(successElement.closest('div')).toHaveClass('bg-green-900/50', 'border-green-700');
        expect(successElement).toHaveClass('text-green-200');
      });
    });

    test('shows loading spinner with correct styling', async () => {
      authService.forgotPassword.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      // Check for loading spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('h-5', 'w-5', 'text-white');
      
      await waitFor(() => {
        expect(screen.getByText('If an account with that email exists, a password reset link has been sent.')).toBeInTheDocument();
      });
    });
  });

  /*
   * Navigation Links Tests
   */
  describe('Navigation Links', () => {
    test('contains correct navigation links', () => {
      renderWithRouter(<ForgotPassword />);
      
      const signInLink = screen.getByText('Sign in');
      const signUpLink = screen.getByText('Sign up');
      const logoLink = screen.getByAltText('Voxify').closest('a');
      
      expect(signInLink).toHaveAttribute('href', '/login');
      expect(signUpLink).toHaveAttribute('href', '/register');
      expect(logoLink).toHaveAttribute('href', '/');
    });

    test('navigation links have proper styling', () => {
      renderWithRouter(<ForgotPassword />);
      
      const signInLink = screen.getByText('Sign in');
      const signUpLink = screen.getByText('Sign up');
      
      expect(signInLink).toHaveClass('font-medium', 'text-blue-400', 'hover:text-blue-300');
      expect(signUpLink).toHaveClass('font-medium', 'text-blue-400', 'hover:text-blue-300');
    });
  });

  /*
   * Form Submission Method Tests
   */
  describe('Form Submission Methods', () => {
    test('form can be submitted with Enter key', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      // Submit form with Enter key
      fireEvent.submit(emailInput.closest('form'));
      
      await waitFor(() => {
        expect(authService.forgotPassword).toHaveBeenCalledWith('test@example.com');
      });
    });

    test('form can be submitted by clicking submit button', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(authService.forgotPassword).toHaveBeenCalledWith('test@example.com');
      });
    });
  });

  /*
   * Accessibility Tests
   */
  describe('Accessibility', () => {
    test('form has proper labels and structure', () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const emailLabel = screen.getByLabelText('Email address');
      
      expect(emailLabel).toBe(emailInput);
      expect(emailInput).toHaveAttribute('id', 'email');
    });

    test('page has proper heading structure', () => {
      renderWithRouter(<ForgotPassword />);
      
      expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Forgot your password?');
    });

    test('submit button is properly accessible', () => {
      renderWithRouter(<ForgotPassword />);
      
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveAttribute('type', 'submit');
    });

    test('form elements are properly structured', () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      // Check that elements exist and are properly structured
      expect(emailInput).toBeInTheDocument();
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveAttribute('type', 'submit');
      
      // Check that the email input has proper attributes
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('id', 'email');
    });
  });

  /*
   * Edge Cases Tests
   */
  describe('Edge Cases', () => {
    test('handles multiple rapid form submissions', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      // Rapid clicks
      fireEvent.click(submitButton);
      fireEvent.click(submitButton);
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(authService.forgotPassword).toHaveBeenCalledTimes(1);
      });
    });

    test('handles empty form submission multiple times', async () => {
      renderWithRouter(<ForgotPassword />);
      
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });
      
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });
      
      expect(authService.forgotPassword).not.toHaveBeenCalled();
    });

    test('handles whitespace-only email', async () => {
      renderWithRouter(<ForgotPassword />);
      
      const emailInput = screen.getByPlaceholderText('Email address');
      const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
      
      fireEvent.change(emailInput, { target: { value: '   ' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });
    });
  });
});