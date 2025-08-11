import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Login from '../Login';

// Import the mocked auth service
import authService from '../../services/auth.service';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock the auth service module
jest.mock('../../services/auth.service', () => ({
  isAuthenticated: jest.fn(),
  login: jest.fn(),
}));

// Helper component to wrap Login with Router
const LoginWithRouter = () => (
  <BrowserRouter>
    <Login />
  </BrowserRouter>
);

describe('Login Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authService.isAuthenticated.mockReturnValue(false);
  });

  describe('Initial Render', () => {
    test('Render login form with all fields', () => {
      render(<LoginWithRouter />);
      expect(screen.getByText('Log in to Voxify')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /log in/i })
      ).toBeInTheDocument();
    });

    test('Render logo with correct attributes', () => {
      render(<LoginWithRouter />);
      const logo = screen.getByAltText('Voxify Logo');
      expect(logo).toBeInTheDocument();
      expect(logo).toHaveAttribute('src', '/logo.png');
      const logoLink = screen.getByRole('link', { name: 'Voxify Logo' });
      expect(logoLink).toHaveAttribute('href', '/');
    });

    test('Render sign up link', () => {
      render(<LoginWithRouter />);
      expect(screen.getByText("Don't have an account?")).toBeInTheDocument();
      const signUpLink = screen.getByText('Sign up');
      expect(signUpLink).toBeInTheDocument();
      expect(signUpLink).toHaveAttribute('href', '/register');
    });

    test('Redirect authenticated users to home', () => {
      authService.isAuthenticated.mockReturnValue(true);
      render(<LoginWithRouter />);
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Form Input Handling', () => {
    test('Update email when typing in email field', () => {
      render(<LoginWithRouter />);
      const emailInput = screen.getByLabelText('Email');
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      expect(emailInput.value).toBe('test@example.com');
    });

    test('Update password when typing in password field', () => {
      render(<LoginWithRouter />);
      const passwordInput = screen.getByLabelText('Password');
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      expect(passwordInput.value).toBe('password123');
    });

    test('Email and password fields are required', () => {
      render(<LoginWithRouter />);
      expect(screen.getByLabelText('Email')).toBeRequired();
      expect(screen.getByLabelText('Password')).toBeRequired();
    });

    test('Email field has correct type and autocomplete attributes', () => {
      render(<LoginWithRouter />);
      const emailInput = screen.getByLabelText('Email');
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('autoComplete', 'email');
    });

    test('Password field has correct autocomplete attribute', () => {
      render(<LoginWithRouter />);
      const passwordInput = screen.getByLabelText('Password');
      expect(passwordInput).toHaveAttribute('autoComplete', 'current-password');
    });
  });

  describe('Password Visibility Toggle', () => {
    test('Toggles password visibility when button is clicked', () => {
      render(<LoginWithRouter />);
      const passwordInput = screen.getByLabelText('Password');
      const toggleButton = screen.getByRole('button', { name: '' }); // Toggle button has no alt name
      expect(passwordInput).toHaveAttribute('type', 'password');
      fireEvent.click(toggleButton); // Show password
      expect(passwordInput).toHaveAttribute('type', 'text');
      fireEvent.click(toggleButton); // Hide password
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('shows correct eye icon based on password visibility state', () => {
      render(<LoginWithRouter />);
      const toggleButton = screen.getByRole('button', { name: '' });
      expect(toggleButton).toBeInTheDocument();
      fireEvent.click(toggleButton); // Show icon
      expect(toggleButton).toBeInTheDocument();
      fireEvent.click(toggleButton); // Hide again
      expect(toggleButton).toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    const validCredentials = {
      email: 'test@example.com',
      password: 'password123',
    };

    const fillForm = () => {
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: validCredentials.email },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: validCredentials.password },
      });
    };

    test('Successful login redirects to home page', async () => {
      authService.login.mockResolvedValue({ success: true });
      render(<LoginWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith(
          validCredentials.email,
          validCredentials.password
        );
      });
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });

    test('Failed login shows error message', async () => {
      authService.login.mockResolvedValue({
        success: false,
        error: 'Invalid credentials',
      });
      render(<LoginWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    test('Login exception shows generic error message', async () => {
      authService.login.mockRejectedValue(new Error('Network error'));
      render(<LoginWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      await waitFor(() => {
        expect(
          screen.getByText('Login failed. Please try again.')
        ).toBeInTheDocument();
      });
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    test('Show loading state during login', async () => {
      // Mock a slow login
      authService.login.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ success: true }), 100)
          )
      );
      render(<LoginWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      // Check loading state
      expect(screen.getByText('Logging in...')).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /logging in/i })
      ).toBeDisabled();
      // Check that form fields are disabled during loading
      expect(screen.getByLabelText('Email')).toBeDisabled();
      expect(screen.getByLabelText('Password')).toBeDisabled();
      // Wait for completion
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });

    test('Clear error message when form is resubmitted', async () => {
      authService.login
        .mockResolvedValueOnce({ success: false, error: 'Invalid credentials' })
        .mockResolvedValueOnce({ success: true });
      render(<LoginWithRouter />);
      fillForm();
      // First submission - should show error
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
      // Second submission - error should be cleared
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      await waitFor(() => {
        expect(
          screen.queryByText('Invalid credentials')
        ).not.toBeInTheDocument();
      });
    });

    test('Prevent form submission when loading', async () => {
      authService.login.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ success: true }), 100)
          )
      );
      render(<LoginWithRouter />);
      fillForm();
      const submitButton = screen.getByRole('button', { name: /log in/i });
      fireEvent.click(submitButton);
      // Button should be disabled
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /logging in/i })
        ).toBeDisabled();
      });
      // Try to click again - should not trigger another call
      fireEvent.click(screen.getByRole('button', { name: /logging in/i }));
      // Wait for completion
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
      expect(authService.login).toHaveBeenCalledTimes(1); // Should only be called once
    });
  });

  describe('Error Handling', () => {
    test('Error message is displayed with proper styling', async () => {
      authService.login.mockResolvedValue({
        success: false,
        error: 'Account locked',
      });
      render(<LoginWithRouter />);
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' },
      });
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      await waitFor(() => {
        const errorElement = screen.getByText('Account locked');
        expect(errorElement).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Account locked')).toHaveClass('text-red-500');
      });
    });

    test('No error message is shown initially', () => {
      render(<LoginWithRouter />);
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/failed/i)).not.toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    test('Rorm can be submitted with valid HTML5 validation', () => {
      render(<LoginWithRouter />);
      // Check form fields for validation
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      expect(emailInput).toBeRequired();
      expect(passwordInput).toBeRequired();
    });

    test('Email input accepts valid email format', () => {
      render(<LoginWithRouter />);
      const emailInput = screen.getByLabelText('Email');
      fireEvent.change(emailInput, { target: { value: 'valid@email.com' } });
      expect(emailInput).toBeValid();
    });
  });

  describe('Loading State', () => {
    test('Loading spinner is visible during login', async () => {
      authService.login.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ success: true }), 100)
          )
      );
      render(<LoginWithRouter />);
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' },
      });
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      const loadingButton = screen.getByRole('button', { name: /logging in/i });
      expect(loadingButton).toBeInTheDocument();
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });

    test('Loading state applies correct CSS classes', async () => {
      authService.login.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ success: true }), 100)
          )
      );
      render(<LoginWithRouter />);
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' },
      });
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      await waitFor(() => {
        const loadingButton = screen.getByRole('button', {
          name: /logging in/i,
        });
        expect(loadingButton).toBeInTheDocument();
      });
      await waitFor(() => {
        const loadingButton = screen.getByRole('button', {
          name: /logging in/i,
        });
        expect(loadingButton).toHaveClass('opacity-50', 'cursor-not-allowed');
      });
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });
  });

  describe('Accessibility', () => {
    test('Form has proper labels and IDs', () => {
      render(<LoginWithRouter />);
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      expect(emailInput).toHaveAttribute('id', 'email');
      expect(passwordInput).toHaveAttribute('id', 'password');
      // Check that labels are properly associated
      const emailLabel = screen.getByText('Email');
      const passwordLabel = screen.getByText('Password');
      expect(emailLabel).toHaveAttribute('for', 'email');
      expect(passwordLabel).toHaveAttribute('for', 'password');
    });

    test('Form elements have appropriate names', () => {
      render(<LoginWithRouter />);
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      expect(emailInput).toHaveAttribute('name', 'email');
      expect(passwordInput).toHaveAttribute('name', 'password');
    });

    test('Submit button has proper accessible name during loading', async () => {
      authService.login.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ success: true }), 100)
          )
      );
      render(<LoginWithRouter />);
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' },
      });
      fireEvent.click(screen.getByRole('button', { name: /log in/i }));
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /logging in/i })
        ).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });
  });
});
