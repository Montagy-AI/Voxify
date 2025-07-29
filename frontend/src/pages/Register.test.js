import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Register from './Register';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock the auth service module
jest.mock('../services/auth.service', () => ({
  isAuthenticated: jest.fn(),
  register: jest.fn(),
  login: jest.fn(),
}));

// Import the mocked auth service
import authService from '../services/auth.service';

// Helper component to wrap Register with Router
const RegisterWithRouter = () => (
  <BrowserRouter>
    <Register />
  </BrowserRouter>
);

describe('Register Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authService.isAuthenticated.mockReturnValue(false);
  });

  /*
        Test cases for the Register page's initial render.
    */
  describe('Initial Render', () => {
    test('Render registration form with all fields', () => {
      render(<RegisterWithRouter />);
      expect(screen.getByText('Create your account')).toBeInTheDocument();
      expect(screen.getByLabelText('First Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Last Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /create account/i })
      ).toBeInTheDocument();
    });

    test('Render logo with correct attributes', () => {
      render(<RegisterWithRouter />);
      const logo = screen.getByAltText('Voxify Logo');
      expect(logo).toBeInTheDocument();
      expect(logo).toHaveAttribute('src', '/logo.png');
    });

    test('Render login link', () => {
      render(<RegisterWithRouter />);
      expect(screen.getByText('Already have an account?')).toBeInTheDocument();
      expect(screen.getByText('Log in')).toBeInTheDocument();
      expect(screen.getByText('Log in').closest('a')).toHaveAttribute(
        'href',
        '/login'
      );
    });

    test('Redirect authenticated users to home', () => {
      authService.isAuthenticated.mockReturnValue(true);
      render(<RegisterWithRouter />);
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  /*
        Test cases for input handling.
    */
  describe('Form Input Handling', () => {
    test('Update form data when typing in fields', () => {
      render(<RegisterWithRouter />);
      const firstNameInput = screen.getByLabelText('First Name');
      const lastNameInput = screen.getByLabelText('Last Name');
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const confirmPasswordInput = screen.getByLabelText('Confirm Password');

      fireEvent.change(firstNameInput, { target: { value: 'John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'Password123!' } });
      fireEvent.change(confirmPasswordInput, {
        target: { value: 'Password123!' },
      });

      expect(firstNameInput.value).toBe('John');
      expect(lastNameInput.value).toBe('Doe');
      expect(emailInput.value).toBe('john@example.com');
      expect(passwordInput.value).toBe('Password123!');
      expect(confirmPasswordInput.value).toBe('Password123!');
    });

    test('Ensure all form fields are required', () => {
      render(<RegisterWithRouter />);
      expect(screen.getByLabelText('First Name')).toBeRequired();
      expect(screen.getByLabelText('Last Name')).toBeRequired();
      expect(screen.getByLabelText('Email')).toBeRequired();
      expect(screen.getByLabelText('Password')).toBeRequired();
      expect(screen.getByLabelText('Confirm Password')).toBeRequired();
    });
  });

  /*
        Test case for password visibility.
    */
  describe('Password Visibility Toggle', () => {
    test('Toggle password visibility when button is clicked', () => {
      render(<RegisterWithRouter />);
      const passwordInput = screen.getByLabelText('Password');
      const confirmPasswordInput = screen.getByLabelText('Confirm Password');
      const toggleButton = screen.getByRole('button', { name: '' }); // Note: Toggle button has no alt name
      // Initially, password fields should be hidden
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');
      fireEvent.click(toggleButton); // Click to show password
      expect(passwordInput).toHaveAttribute('type', 'text');
      expect(confirmPasswordInput).toHaveAttribute('type', 'text');
      fireEvent.click(toggleButton); // Click to hide password
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    });
  });

  /*
        Test cases for password requirements.
    */
  describe('Password Requirements', () => {
    test('Show password requirements when password field is focused', () => {
      render(<RegisterWithRouter />);
      const passwordInput = screen.getByLabelText('Password');
      // Requirements should not be visible initially
      expect(
        screen.queryByText('Password must contain:')
      ).not.toBeInTheDocument();
      fireEvent.focus(passwordInput);
      expect(screen.getByText('Password must contain:')).toBeInTheDocument();
      expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
      expect(
        screen.getByText('Contains at least one number')
      ).toBeInTheDocument();
      expect(
        screen.getByText('Contains at least one special character')
      ).toBeInTheDocument();
      expect(
        screen.getByText('Contains at least one uppercase letter')
      ).toBeInTheDocument();
      expect(
        screen.getByText('Contains at least one lowercase letter')
      ).toBeInTheDocument();
    });

    test('Hide password requirements when password field is blurred and empty', () => {
      render(<RegisterWithRouter />);
      const passwordInput = screen.getByLabelText('Password');
      fireEvent.focus(passwordInput);
      expect(screen.getByText('Password must contain:')).toBeInTheDocument();
      fireEvent.blur(passwordInput);
      expect(
        screen.queryByText('Password must contain:')
      ).not.toBeInTheDocument();
    });

    test('Keep password requirements visible when password field has value', () => {
      render(<RegisterWithRouter />);
      const passwordInput = screen.getByLabelText('Password');
      fireEvent.change(passwordInput, { target: { value: 'test' } });
      fireEvent.focus(passwordInput);
      fireEvent.blur(passwordInput);
      expect(screen.getByText('Password must contain:')).toBeInTheDocument();
    });

    test('Validate password requirements correctly', () => {
      render(<RegisterWithRouter />);
      const passwordInput = screen.getByLabelText('Password');
      fireEvent.focus(passwordInput);
      // Test weak password
      fireEvent.change(passwordInput, { target: { value: 'weak' } });
      const validationItems = screen.getAllByRole('listitem');
      // All should show X (invalid) initially
      validationItems.forEach((item) => {
        const svg = item.querySelector('svg');
        expect(svg).toBeInTheDocument();
      });
      // Test strong password
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123!' } });
      // All validations should pass
      const lengthItem = screen
        .getByText('At least 8 characters')
        .closest('li');
      expect(lengthItem.querySelector('.text-green-500')).toBeInTheDocument();
    });
  });

  /*
        Test cases for form validation.
    */
  describe('Form Validation', () => {
    test('Show error when passwords do not match', async () => {
      render(<RegisterWithRouter />);
      fireEvent.change(screen.getByLabelText('First Name'), {
        target: { value: 'John' },
      });
      fireEvent.change(screen.getByLabelText('Last Name'), {
        target: { value: 'Doe' },
      });
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'john@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'Password123!' },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'DifferentPassword!' },
      });
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
      });
    });

    test('Show error when password is too short', async () => {
      render(<RegisterWithRouter />);
      fireEvent.change(screen.getByLabelText('First Name'), {
        target: { value: 'John' },
      });
      fireEvent.change(screen.getByLabelText('Last Name'), {
        target: { value: 'Doe' },
      });
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'john@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'short' },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'short' },
      });
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      await waitFor(() => {
        expect(
          screen.getByText('Password must be at least 8 characters long')
        ).toBeInTheDocument();
      });
    });
  });

  /*
        Test cases for form submission correctly handling.
    */
  describe('Form Submission', () => {
    const validFormData = {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com',
      password: 'Password123!',
      confirmPassword: 'Password123!',
    };

    const fillForm = () => {
      fireEvent.change(screen.getByLabelText('First Name'), {
        target: { value: validFormData.firstName },
      });
      fireEvent.change(screen.getByLabelText('Last Name'), {
        target: { value: validFormData.lastName },
      });
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: validFormData.email },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: validFormData.password },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: validFormData.confirmPassword },
      });
    };

    test('Successful registration and login redirects to home', async () => {
      authService.register.mockResolvedValue({ success: true });
      authService.login.mockResolvedValue({ success: true });
      render(<RegisterWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          email: validFormData.email,
          password: validFormData.password,
          firstName: validFormData.firstName,
          lastName: validFormData.lastName,
        });
      });
      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith(
          validFormData.email,
          validFormData.password
        );
      });
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    test('Successful registration but failed login redirects to login page', async () => {
      authService.register.mockResolvedValue({ success: true });
      authService.login.mockResolvedValue({ success: false });
      render(<RegisterWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });

    test('Show error message when registration fails', async () => {
      authService.register.mockResolvedValue({
        success: false,
        error: 'Email already exists',
      });
      render(<RegisterWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeInTheDocument();
      });
    });

    test('Show generic error message when registration throws exception', async () => {
      authService.register.mockRejectedValue(new Error('Network error'));
      render(<RegisterWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      await waitFor(() => {
        expect(
          screen.getByText('Registration failed. Please try again.')
        ).toBeInTheDocument();
      });
    });

    test('Show loading state during registration', async () => {
      // Mock a slow registration
      authService.register.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ success: true }), 100)
          )
      );
      authService.login.mockResolvedValue({ success: true });
      render(<RegisterWithRouter />);
      fillForm();
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      // Check loading state
      expect(screen.getByText('Creating account...')).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /creating account/i })
      ).toBeDisabled();
      // Check that form fields are disabled during loading
      expect(screen.getByLabelText('First Name')).toBeDisabled();
      expect(screen.getByLabelText('Last Name')).toBeDisabled();
      expect(screen.getByLabelText('Email')).toBeDisabled();
      expect(screen.getByLabelText('Password')).toBeDisabled();
      expect(screen.getByLabelText('Confirm Password')).toBeDisabled();
      // Wait for completion
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });

    test('Clear error message when form is resubmitted', async () => {
      authService.register
        .mockResolvedValueOnce({
          success: false,
          error: 'Email already exists',
        })
        .mockResolvedValueOnce({ success: true });
      authService.login.mockResolvedValue({ success: true });
      render(<RegisterWithRouter />);
      fillForm();
      // First submission - should show error
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeInTheDocument();
      });
      // Second submission - error should be cleared
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));
      await waitFor(() => {
        expect(
          screen.queryByText('Email already exists')
        ).not.toBeInTheDocument();
      });
    });
  });

  /*
        Test cases for accessibility.
    */
  describe('Accessibility', () => {
    test('form fields have proper labels and accessibility attributes', () => {
      render(<RegisterWithRouter />);

      const firstNameInput = screen.getByLabelText('First Name');
      const lastNameInput = screen.getByLabelText('Last Name');
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const confirmPasswordInput = screen.getByLabelText('Confirm Password');

      expect(firstNameInput).toHaveAttribute('id', 'firstName');
      expect(lastNameInput).toHaveAttribute('id', 'lastName');
      expect(emailInput).toHaveAttribute('id', 'email');
      expect(passwordInput).toHaveAttribute('id', 'password');
      expect(confirmPasswordInput).toHaveAttribute('id', 'confirmPassword');

      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('autoComplete', 'email');
      expect(passwordInput).toHaveAttribute('autoComplete', 'new-password');
      expect(confirmPasswordInput).toHaveAttribute(
        'autoComplete',
        'new-password'
      );
    });

    test('Submit button has proper loading aria attributes', async () => {
      authService.register.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ success: true }), 100)
          )
      );
      authService.login.mockResolvedValue({ success: true });
      render(<RegisterWithRouter />);
      const submitButton = screen.getByRole('button', {
        name: /create account/i,
      });
      expect(submitButton).not.toBeDisabled();

      fireEvent.change(screen.getByLabelText('First Name'), {
        target: { value: 'John' },
      });
      fireEvent.change(screen.getByLabelText('Last Name'), {
        target: { value: 'Doe' },
      });
      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'john@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'Password123!' },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'Password123!' },
      });

      fireEvent.click(submitButton);
      await waitFor(() => {
        const loadingButton = screen.getByRole('button', {
          name: /creating account/i,
        });
        expect(loadingButton).toBeDisabled();
      });
    });
  });
});
