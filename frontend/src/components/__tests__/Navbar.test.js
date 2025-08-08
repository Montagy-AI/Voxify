import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Navbar from '../Navbar';
import authService from '../../services/auth.service';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock auth service module
jest.mock('../../services/auth.service', () => ({
  getCurrentUser: jest.fn(),
  isAuthenticated: jest.fn(),
  logout: jest.fn(),
}));

// Helper component to wrap Navbar with Router
const NavbarWithRouter = () => (
  <BrowserRouter>
    <Navbar />
  </BrowserRouter>
);

describe('Navbar Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /*
        Test cases for unauthenticated user
    */
  describe('Unauthenticated User', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(false);
      authService.getCurrentUser.mockReturnValue(null);
    });

    test('Render logo for unauthenticated user', () => {
      render(<NavbarWithRouter />);
      const logo = screen.getByAltText('Voxify Logo');
      expect(logo).toBeInTheDocument();
      expect(logo).toHaveAttribute('src', '/logo.png');
    });

    test('Show login and register buttons when not authenticated', () => {
      render(<NavbarWithRouter />);
      expect(screen.getByText('Log in')).toBeInTheDocument();
      expect(screen.getByText('Get started')).toBeInTheDocument();
    });

    test('Do not show navigation links when not authenticated', () => {
      render(<NavbarWithRouter />);
      expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
      expect(screen.queryByText('Tasks')).not.toBeInTheDocument();
      expect(screen.queryByText('Voices')).not.toBeInTheDocument();
      expect(screen.queryByText('Settings')).not.toBeInTheDocument();
    });

    test('Do not show help button and profile when not authenticated', () => {
      render(<NavbarWithRouter />);
      // Help button shouldn't be visible
      const helpButtons = screen.queryAllByRole('button');
      expect(helpButtons).toHaveLength(0);
    });
  });

  /*
        Test cases for authenticated user
    */
  describe('Authenticated User', () => {
    const mockUser = {
      first_name: 'John',
      email: 'john@example.com',
      profile_image: null,
    };

    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true);
      authService.getCurrentUser.mockReturnValue(mockUser);
    });

    test('Render navigation links when authenticated', () => {
      render(<NavbarWithRouter />);
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Tasks')).toBeInTheDocument();
      expect(screen.getByText('Voices')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    test('Show help button when authenticated', () => {
      render(<NavbarWithRouter />);
      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(2); // help button and profile button
      // The first button should be the help button (with SVG)
      const helpButton = buttons[0];
      expect(helpButton).toBeInTheDocument();
    });

    test('Show user profile button with first name initial', () => {
      render(<NavbarWithRouter />);
      const profileButton = screen.getByText('J');
      expect(profileButton).toBeInTheDocument();
    });

    test('Show user profile image when available', () => {
      const userWithImage = {
        ...mockUser,
        profile_image: 'https://example.com/profile.jpg',
      };
      authService.getCurrentUser.mockReturnValue(userWithImage);
      render(<NavbarWithRouter />);
      const profileImage = screen.getByAltText('Profile');
      expect(profileImage).toBeInTheDocument();
      expect(profileImage).toHaveAttribute(
        'src',
        'https://example.com/profile.jpg'
      );
    });

    test('Show default initial when user has no first name', () => {
      const userWithoutName = {
        ...mockUser,
        first_name: null,
      };
      authService.getCurrentUser.mockReturnValue(userWithoutName);
      render(<NavbarWithRouter />);
      expect(screen.getByText('U')).toBeInTheDocument();
    });

    test('does not show login/register buttons when authenticated', () => {
      render(<NavbarWithRouter />);
      expect(screen.queryByText('Log in')).not.toBeInTheDocument();
      expect(screen.queryByText('Get started')).not.toBeInTheDocument();
    });

    test('help button navigates to help page', () => {
      render(<NavbarWithRouter />);
      // Get the first button which should be the help button
      const helpButton = screen.getAllByRole('button')[0];
      fireEvent.click(helpButton);
      expect(mockNavigate).toHaveBeenCalledWith('/help');
    });
  });

  /*
        Test cases for profile dropdown functionality
    */
  describe('Profile Dropdown', () => {
    const mockUser = {
      first_name: 'John',
      email: 'john@example.com',
      profile_image: null,
    };

    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true);
      authService.getCurrentUser.mockReturnValue(mockUser);
    });

    test('Open dropdown when profile button is clicked', () => {
      render(<NavbarWithRouter />);
      const profileButton = screen.getByText('J');
      fireEvent.click(profileButton);
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
      expect(screen.getByText('Log out')).toBeInTheDocument();
    });

    test('Close dropdown when clicking outside', async () => {
      render(<NavbarWithRouter />);
      const profileButton = screen.getByText('J');
      fireEvent.click(profileButton); // Open
      expect(screen.getByText('Log out')).toBeInTheDocument();
      fireEvent.mouseDown(document.body); // Click outside
      await waitFor(() => {
        expect(screen.queryByText('Log out')).not.toBeInTheDocument();
      });
    });

    test('Close dropdown when settings link is clicked', () => {
      render(<NavbarWithRouter />);
      const profileButton = screen.getByText('J');
      fireEvent.click(profileButton);
      const settingsLink = screen.getAllByText('Settings')[1]; // Second one is in dropdown
      fireEvent.click(settingsLink);
      expect(screen.queryByText('Log out')).not.toBeInTheDocument();
    });

    test('Logout button calls auth service and navigates', () => {
      render(<NavbarWithRouter />);
      const profileButton = screen.getByText('J');
      fireEvent.click(profileButton);
      const logoutButton = screen.getByText('Log out');
      fireEvent.click(logoutButton);
      expect(authService.logout).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });

    test('toggles dropdown when profile button is clicked multiple times', () => {
      render(<NavbarWithRouter />);
      const profileButton = screen.getByText('J');
      fireEvent.click(profileButton); // Open dropdown
      expect(screen.getByText('Log out')).toBeInTheDocument();
      fireEvent.click(profileButton); // Close dropdown
      expect(screen.queryByText('Log out')).not.toBeInTheDocument();
    });
  });

  /*
    Test cases for navigation links and href attributes
    */
  describe('Navigation Links', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true);
      authService.getCurrentUser.mockReturnValue({
        first_name: 'John',
        email: 'john@example.com',
      });
    });

    test('All navigation links have correct href attributes', () => {
      render(<NavbarWithRouter />);
      expect(screen.getByRole('link', { name: /dashboard/i })).toHaveAttribute(
        'href',
        '/dashboard'
      );
      expect(screen.getByRole('link', { name: /tasks/i })).toHaveAttribute(
        'href',
        '/tasks/list'
      );
      expect(screen.getByRole('link', { name: /voices/i })).toHaveAttribute(
        'href',
        '/voices'
      );
      expect(screen.getByRole('link', { name: /settings/i })).toHaveAttribute(
        'href',
        '/settings'
      );
    });

    test('Logo link points to home page', () => {
      render(<NavbarWithRouter />);
      const logoLink = screen.getByRole('link', { name: /voxify logo/i });
      expect(logoLink).toHaveAttribute('href', '/');
    });

    test('Login and register links have correct hrefs when not authenticated', () => {
      authService.isAuthenticated.mockReturnValue(false);
      authService.getCurrentUser.mockReturnValue(null);
      render(<NavbarWithRouter />);
      expect(screen.getByRole('link', { name: /log in/i })).toHaveAttribute(
        'href',
        '/login'
      );
      expect(
        screen.getByRole('link', { name: /get started/i })
      ).toHaveAttribute('href', '/register');
    });
  });

  /*
        Test cases for component cleanup and event listeners
    */
  describe('Component Cleanup', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true);
      authService.getCurrentUser.mockReturnValue({
        first_name: 'John',
        email: 'john@example.com',
      });
    });

    test('Removes event listener on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(
        document,
        'removeEventListener'
      );
      const { unmount } = render(<NavbarWithRouter />);
      unmount();
      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        'mousedown',
        expect.any(Function)
      );
      removeEventListenerSpy.mockRestore();
    });
  });
});
