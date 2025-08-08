import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import ResetPassword from '../ResetPassword';

// Mock the auth service
jest.mock('../../services/auth.service', () => ({
  isAuthenticated: jest.fn(),
  resetPassword: jest.fn(),
}));

// Mock react-router-dom hooks
const mockNavigate = jest.fn();
const mockSearchParams = new URLSearchParams();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useSearchParams: () => [mockSearchParams],
}));

// Import the mocked service
import authService from '../../services/auth.service';

// Helper function to render component with router
const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('ResetPassword Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSearchParams.delete('token');
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
      mockSearchParams.set('token', 'valid-token');
      
      renderWithRouter(<ResetPassword />);
      
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  /*
   * Token Validation Tests
   */
  describe('Token Validation', () => {
    test('shows error when no token is provided in URL', () => {
      // No token in URL
      renderWithRouter(<ResetPassword />);
      
      expect(screen.getByText('Invalid Reset Link')).toBeInTheDocument();
      expect(screen.getByText('This password reset link is invalid or has expired.')).toBeInTheDocument();
      expect(screen.getByText('Request New Reset Link')).toBeInTheDocument();
      expect(screen.getByText('Back to Login')).toBeInTheDocument();
    });

    test('displays form when valid token is provided', () => {
      mockSearchParams.set('token', 'valid-reset-token');
      
      renderWithRouter(<ResetPassword />);
      
      expect(screen.getByText('Reset your password')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('New password')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Confirm new password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Reset Password' })).toBeInTheDocument();
    });
  });

  /*
   * Form Rendering Tests
   */
  describe('Form Rendering', () => {
    beforeEach(() => {
      mockSearchParams.set('token', 'valid-token');
    });

    test('renders all form elements correctly', () => {
      renderWithRouter(<ResetPassword />);
      
      expect(screen.getByText('Reset your password')).toBeInTheDocument();
      expect(screen.getByText('Enter your new password below.')).toBeInTheDocument();
      
      // Form inputs
      expect(screen.getByPlaceholderText('New password')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Confirm new password')).toBeInTheDocument();
      
      // Password requirements
      expect(screen.getByText('Password must contain:')).toBeInTheDocument();
      expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
      expect(screen.getByText('One uppercase letter')).toBeInTheDocument();
      expect(screen.getByText('One lowercase letter')).toBeInTheDocument();
      expect(screen.getByText('One number')).toBeInTheDocument();
      expect(screen.getByText('One special character')).toBeInTheDocument();
      
      // Submit button
      expect(screen.getByRole('button', { name: 'Reset Password' })).toBeInTheDocument();
      
      // Link to login
      expect(screen.getByText('Remember your password?')).toBeInTheDocument();
      expect(screen.getByText('Sign in')).toBeInTheDocument();
    });

    test('renders logo and navigation links in error state', () => {
      // Remove token to trigger error state
      mockSearchParams.delete('token');
      
      renderWithRouter(<ResetPassword />);
      
      expect(screen.getByAltText('Voxify')).toBeInTheDocument();
      expect(screen.getByText('Request New Reset Link')).toBeInTheDocument();
      expect(screen.getByText('Back to Login')).toBeInTheDocument();
    });
  });

  /*
   * Password Visibility Toggle Tests
   */
  describe('Password Visibility Toggle', () => {
    beforeEach(() => {
      mockSearchParams.set('token', 'valid-token');
    });

    test('toggles password visibility for new password field', () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const toggleButtons = screen.getAllByRole('button', { name: '' }); // Eye icons don't have accessible names
      const passwordToggle = toggleButtons[0]; // First toggle button
      
      // Initially should be password type
      expect(passwordInput).toHaveAttribute('type', 'password');
      
      // Click to show password
      fireEvent.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'text');
      
      // Click to hide password
      fireEvent.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('toggles password visibility for confirm password field', () => {
      renderWithRouter(<ResetPassword />);
      
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const toggleButtons = screen.getAllByRole('button', { name: '' }); // Eye icons don't have accessible names
      const confirmPasswordToggle = toggleButtons[1]; // Second toggle button
      
      // Initially should be password type
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');
      
      // Click to show password
      fireEvent.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute('type', 'text');
      
      // Click to hide password
      fireEvent.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    });
  });

  /*
   * Form Input Tests
   */
  describe('Form Input', () => {
    beforeEach(() => {
      mockSearchParams.set('token', 'valid-token');
    });

    test('updates password input value when typed', () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      
      expect(passwordInput.value).toBe('TestPassword123!');
    });

    test('updates confirm password input value when typed', () => {
      renderWithRouter(<ResetPassword />);
      
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      
      expect(confirmPasswordInput.value).toBe('TestPassword123!');
    });
  });

  /*
   * Form Validation Tests
   */
  describe('Form Validation', () => {
    beforeEach(() => {
      mockSearchParams.set('token', 'valid-token');
    });

    test('shows error when password fields are empty', async () => {
      renderWithRouter(<ResetPassword />);
      
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Both password fields are required')).toBeInTheDocument();
      });
    });

    test('shows error when passwords do not match', async () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword123!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
      });
    });

    test('shows error for password less than 8 characters', async () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'Test1!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'Test1!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Password must be at least 8 characters long')).toBeInTheDocument();
      });
    });

    test('shows error for password without uppercase letter', async () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'testpassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'testpassword123!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Password must contain at least one uppercase letter')).toBeInTheDocument();
      });
    });

    test('shows error for password without lowercase letter', async () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TESTPASSWORD123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TESTPASSWORD123!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Password must contain at least one lowercase letter')).toBeInTheDocument();
      });
    });

    test('shows error for password without number', async () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Password must contain at least one number')).toBeInTheDocument();
      });
    });

    test('shows error for password without special character', async () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Password must contain at least one special character')).toBeInTheDocument();
      });
    });
  });

  /*
   * Successful Form Submission Tests
   */
  describe('Successful Form Submission', () => {
    beforeEach(() => {
      mockSearchParams.set('token', 'valid-token');
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    test('successfully resets password and redirects to login', async () => {
      authService.resetPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(authService.resetPassword).toHaveBeenCalledWith('valid-token', 'TestPassword123!');
      });
      
      await waitFor(() => {
        expect(screen.getByText('Password has been reset successfully! Redirecting to login...')).toBeInTheDocument();
      });
      
      // Check that form is cleared
      expect(passwordInput.value).toBe('');
      expect(confirmPasswordInput.value).toBe('');
      
      // Check that button shows redirecting state
      expect(screen.getByText('Redirecting...')).toBeInTheDocument();
      
      // Fast forward time to trigger navigation
      jest.advanceTimersByTime(3000);
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });

    test('shows loading state during form submission', async () => {
      // Mock slow response
      authService.resetPassword.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );
      
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      
      fireEvent.click(submitButton);
      
      // Should show loading state
      expect(screen.getByText('Resetting...')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
      
      // Wait for completion
      await waitFor(() => {
        expect(screen.getByText('Password has been reset successfully! Redirecting to login...')).toBeInTheDocument();
      });
    });
  });

  /*
   * Error Handling Tests
   */
  describe('Error Handling', () => {
    beforeEach(() => {
      mockSearchParams.set('token', 'valid-token');
    });

    test('shows error when reset password API returns error', async () => {
      authService.resetPassword.mockResolvedValue({ 
        success: false, 
        error: 'Token has expired' 
      });
      
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Token has expired')).toBeInTheDocument();
      });
    });

    test('shows generic error when reset password API throws exception', async () => {
      authService.resetPassword.mockRejectedValue(new Error('Network error'));
      
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to reset password. Please try again.')).toBeInTheDocument();
      });
    });
  });

  /*
   * Form State Management Tests
   */
  describe('Form State Management', () => {
    beforeEach(() => {
      mockSearchParams.set('token', 'valid-token');
    });

    test('disables form inputs during submission', async () => {
      authService.resetPassword.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );
      
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      
      fireEvent.click(submitButton);
      
      // Inputs should be disabled during submission
      expect(passwordInput).toBeDisabled();
      expect(confirmPasswordInput).toBeDisabled();
      
      await waitFor(() => {
        expect(screen.getByText('Password has been reset successfully! Redirecting to login...')).toBeInTheDocument();
      });
    });

    test('clears error messages when form is resubmitted', async () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      // First submission with invalid data
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword123!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
      });
      
      // Fix the password and resubmit
      authService.resetPassword.mockResolvedValue({ success: true });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.click(submitButton);
      
      // Error should be cleared
      await waitFor(() => {
        expect(screen.queryByText('Passwords do not match')).not.toBeInTheDocument();
      });
    });
  });

  /*
   * Accessibility Tests
   */
  describe('Accessibility', () => {
    beforeEach(() => {
      mockSearchParams.set('token', 'valid-token');
    });

    test('form inputs have proper labels and attributes', () => {
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      
      expect(passwordInput).toHaveAttribute('id', 'password');
      expect(passwordInput).toHaveAttribute('name', 'password');
      expect(passwordInput).toHaveAttribute('autoComplete', 'new-password');
      expect(passwordInput).toBeRequired();
      
      expect(confirmPasswordInput).toHaveAttribute('id', 'confirmPassword');
      expect(confirmPasswordInput).toHaveAttribute('name', 'confirmPassword');
      expect(confirmPasswordInput).toHaveAttribute('autoComplete', 'new-password');
      expect(confirmPasswordInput).toBeRequired();
    });

    test('submit button has proper disabled states', () => {
      renderWithRouter(<ResetPassword />);
      
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      expect(submitButton).not.toBeDisabled();
      expect(submitButton).toHaveAttribute('type', 'submit');
    });
  });

  /*
   * Edge Cases Tests
   */
  describe('Edge Cases', () => {
    test('handles API error gracefully in form submission', async () => {
      mockSearchParams.set('token', 'valid-token');
      // Mock API to throw an error
      authService.resetPassword.mockRejectedValue(new Error('Network error'));
      
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      const submitButton = screen.getByRole('button', { name: 'Reset Password' });
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to reset password. Please try again.')).toBeInTheDocument();
      });
    });

    test('form can be submitted with Enter key', async () => {
      mockSearchParams.set('token', 'valid-token');
      authService.resetPassword.mockResolvedValue({ success: true });
      
      renderWithRouter(<ResetPassword />);
      
      const passwordInput = screen.getByPlaceholderText('New password');
      const confirmPasswordInput = screen.getByPlaceholderText('Confirm new password');
      
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      
      // Submit form with Enter key
      fireEvent.submit(passwordInput.closest('form'));
      
      await waitFor(() => {
        expect(authService.resetPassword).toHaveBeenCalledWith('valid-token', 'TestPassword123!');
      });
    });
  });
});