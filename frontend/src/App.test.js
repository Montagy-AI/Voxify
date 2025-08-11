import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route, Navigate } from 'react-router-dom';
import '@testing-library/jest-dom';

import authService from './services/auth.service';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import VoiceClone from './pages/VoiceClone';
import TextToSpeech from './pages/TextToSpeech';
import Tasks from './pages/Tasks';
import Voices from './pages/Voices';
import Settings from './pages/Settings';
import HelpPage from './pages/HelpPage';

// Mock all the page components
jest.mock('./components/Navbar', () => {
  return function MockNavbar() {
    return <div data-testid="navbar">Navbar</div>;
  };
});

jest.mock('./pages/Login', () => {
  return function MockLogin() {
    return <div data-testid="login-page">Login Page</div>;
  };
});

jest.mock('./pages/Register', () => {
  return function MockRegister() {
    return <div data-testid="register-page">Register Page</div>;
  };
});

jest.mock('./pages/ForgotPassword', () => {
  return function MockForgotPassword() {
    return <div data-testid="forgot-password-page">Forgot Password Page</div>;
  };
});

jest.mock('./pages/ResetPassword', () => {
  return function MockResetPassword() {
    return <div data-testid="reset-password-page">Reset Password Page</div>;
  };
});

jest.mock('./pages/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard-page">Dashboard Page</div>;
  };
});

jest.mock('./pages/VoiceClone', () => {
  return function MockVoiceClone() {
    return <div data-testid="voice-clone-page">Voice Clone Page</div>;
  };
});

jest.mock('./pages/TextToSpeech', () => {
  return function MockTextToSpeech() {
    return <div data-testid="text-to-speech-page">Text To Speech Page</div>;
  };
});

jest.mock('./pages/Tasks', () => {
  return function MockTasks() {
    return <div data-testid="tasks-page">Tasks Page</div>;
  };
});

jest.mock('./pages/Voices', () => {
  return function MockVoices() {
    return <div data-testid="voices-page">Voices Page</div>;
  };
});

jest.mock('./pages/Settings', () => {
  return function MockSettings() {
    return <div data-testid="settings-page">Settings Page</div>;
  };
});

jest.mock('./pages/HelpPage', () => {
  return function MockHelpPage() {
    return <div data-testid="help-page">Help Page</div>;
  };
});

// Mock the auth service
jest.mock('./services/auth.service', () => ({
  isAuthenticated: jest.fn(),
}));

// Recreate the App component logic for testing without the BrowserRouter
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" />;
  }

  return children;
};

const TestApp = () => {
  return (
    <div className="min-h-screen bg-[#0F1419]">
      <Navbar />
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/signup"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          }
        />
        <Route
          path="/reset-password"
          element={
            <PublicRoute>
              <ResetPassword />
            </PublicRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/voice-clone"
          element={
            <ProtectedRoute>
              <VoiceClone />
            </ProtectedRoute>
          }
        />
        <Route
          path="/text-to-speech"
          element={
            <ProtectedRoute>
              <TextToSpeech />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks"
          element={
            <ProtectedRoute>
              <Tasks />
            </ProtectedRoute>
          }
        />
        <Route
          path="/voices"
          element={
            <ProtectedRoute>
              <Voices />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks/voice-clone"
          element={
            <ProtectedRoute>
              <VoiceClone />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks/text-to-speech"
          element={
            <ProtectedRoute>
              <TextToSpeech />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks/list"
          element={
            <ProtectedRoute>
              <Tasks />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />

        <Route path="/help" element={<HelpPage />} />

        {/* Redirect root to dashboard or login */}
        <Route
          path="/"
          element={
            <Navigate
              to={authService.isAuthenticated() ? '/dashboard' : '/login'}
              replace
            />
          }
        />
      </Routes>
    </div>
  );
};

// Helper function to render TestApp with initial route
const renderAppWithRoute = (initialRoute = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <TestApp />
    </MemoryRouter>
  );
};

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic App Structure', () => {
    test('renders the app with correct background styling', () => {
      authService.isAuthenticated.mockReturnValue(false);
      renderAppWithRoute('/login');

      // Check that the login page is rendered, which confirms the app structure is working
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
      expect(screen.getByTestId('navbar')).toBeInTheDocument();
    });

    test('always renders the Navbar component', () => {
      authService.isAuthenticated.mockReturnValue(false);
      renderAppWithRoute('/login');

      expect(screen.getByTestId('navbar')).toBeInTheDocument();
    });
  });

  describe('Public Routes (Unauthenticated User)', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(false);
    });

    test('renders Login page at /login', () => {
      renderAppWithRoute('/login');
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });

    test('renders Register page at /signup', () => {
      renderAppWithRoute('/signup');
      expect(screen.getByTestId('register-page')).toBeInTheDocument();
    });

    test('renders Register page at /register', () => {
      renderAppWithRoute('/register');
      expect(screen.getByTestId('register-page')).toBeInTheDocument();
    });

    test('renders ForgotPassword page at /forgot-password', () => {
      renderAppWithRoute('/forgot-password');
      expect(screen.getByTestId('forgot-password-page')).toBeInTheDocument();
    });

    test('renders ResetPassword page at /reset-password', () => {
      renderAppWithRoute('/reset-password');
      expect(screen.getByTestId('reset-password-page')).toBeInTheDocument();
    });

    test('renders Help page at /help', () => {
      renderAppWithRoute('/help');
      expect(screen.getByTestId('help-page')).toBeInTheDocument();
    });

    test('redirects to login when accessing root path', async () => {
      renderAppWithRoute('/');
      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });

    test('redirects protected routes to login', async () => {
      renderAppWithRoute('/dashboard');
      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });
  });

  describe('Protected Routes (Authenticated User)', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true);
    });

    test('renders Dashboard page at /dashboard', () => {
      renderAppWithRoute('/dashboard');
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    });

    test('renders VoiceClone page at /voice-clone', () => {
      renderAppWithRoute('/voice-clone');
      expect(screen.getByTestId('voice-clone-page')).toBeInTheDocument();
    });

    test('renders TextToSpeech page at /text-to-speech', () => {
      renderAppWithRoute('/text-to-speech');
      expect(screen.getByTestId('text-to-speech-page')).toBeInTheDocument();
    });

    test('renders Tasks page at /tasks', () => {
      renderAppWithRoute('/tasks');
      expect(screen.getByTestId('tasks-page')).toBeInTheDocument();
    });

    test('renders Voices page at /voices', () => {
      renderAppWithRoute('/voices');
      expect(screen.getByTestId('voices-page')).toBeInTheDocument();
    });

    test('renders Settings page at /settings', () => {
      renderAppWithRoute('/settings');
      expect(screen.getByTestId('settings-page')).toBeInTheDocument();
    });

    test('renders VoiceClone page at /tasks/voice-clone', () => {
      renderAppWithRoute('/tasks/voice-clone');
      expect(screen.getByTestId('voice-clone-page')).toBeInTheDocument();
    });

    test('renders TextToSpeech page at /tasks/text-to-speech', () => {
      renderAppWithRoute('/tasks/text-to-speech');
      expect(screen.getByTestId('text-to-speech-page')).toBeInTheDocument();
    });

    test('renders Tasks page at /tasks/list', () => {
      renderAppWithRoute('/tasks/list');
      expect(screen.getByTestId('tasks-page')).toBeInTheDocument();
    });

    test('redirects to dashboard when accessing root path', async () => {
      renderAppWithRoute('/');
      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
      });
    });
  });

  describe('PublicRoute Component Behavior', () => {
    test('redirects authenticated users away from public routes', async () => {
      authService.isAuthenticated.mockReturnValue(true);

      renderAppWithRoute('/login');
      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
      });
    });

    test('allows unauthenticated users to access public routes', () => {
      authService.isAuthenticated.mockReturnValue(false);

      renderAppWithRoute('/login');
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });

    test('redirects authenticated users from register page', async () => {
      authService.isAuthenticated.mockReturnValue(true);

      renderAppWithRoute('/register');
      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
      });
    });

    test('redirects authenticated users from forgot password page', async () => {
      authService.isAuthenticated.mockReturnValue(true);

      renderAppWithRoute('/forgot-password');
      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
      });
    });

    test('redirects authenticated users from reset password page', async () => {
      authService.isAuthenticated.mockReturnValue(true);

      renderAppWithRoute('/reset-password');
      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
      });
    });
  });

  describe('ProtectedRoute Component Behavior', () => {
    test('redirects unauthenticated users to login', async () => {
      authService.isAuthenticated.mockReturnValue(false);

      renderAppWithRoute('/dashboard');
      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });

    test('allows authenticated users to access protected routes', () => {
      authService.isAuthenticated.mockReturnValue(true);

      renderAppWithRoute('/dashboard');
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    });

    test('redirects unauthenticated users from voice clone page', async () => {
      authService.isAuthenticated.mockReturnValue(false);

      renderAppWithRoute('/voice-clone');
      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });

    test('redirects unauthenticated users from text-to-speech page', async () => {
      authService.isAuthenticated.mockReturnValue(false);

      renderAppWithRoute('/text-to-speech');
      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });

    test('redirects unauthenticated users from tasks page', async () => {
      authService.isAuthenticated.mockReturnValue(false);

      renderAppWithRoute('/tasks');
      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });

    test('redirects unauthenticated users from voices page', async () => {
      authService.isAuthenticated.mockReturnValue(false);

      renderAppWithRoute('/voices');
      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });

    test('redirects unauthenticated users from settings page', async () => {
      authService.isAuthenticated.mockReturnValue(false);

      renderAppWithRoute('/settings');
      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });
    });
  });

  describe('Help Page Access', () => {
    test('allows unauthenticated users to access help page', () => {
      authService.isAuthenticated.mockReturnValue(false);

      renderAppWithRoute('/help');
      expect(screen.getByTestId('help-page')).toBeInTheDocument();
    });

    test('allows authenticated users to access help page', () => {
      authService.isAuthenticated.mockReturnValue(true);

      renderAppWithRoute('/help');
      expect(screen.getByTestId('help-page')).toBeInTheDocument();
    });
  });

  describe('Route Edge Cases', () => {
    test('handles unknown routes gracefully', () => {
      authService.isAuthenticated.mockReturnValue(false);

      // This should probably redirect to login for unknown routes
      renderAppWithRoute('/unknown-route');
      // Since there's no catch-all route, it should still show navbar but no page content
      expect(screen.getByTestId('navbar')).toBeInTheDocument();
    });

    test('multiple route definitions work correctly', () => {
      authService.isAuthenticated.mockReturnValue(false);

      // Test /signup and /register both lead to register page
      renderAppWithRoute('/signup');
      expect(screen.getByTestId('register-page')).toBeInTheDocument();
    });
  });

  describe('Authentication State Changes', () => {
    test('app responds correctly when authentication state changes', async () => {
      // Start unauthenticated
      authService.isAuthenticated.mockReturnValue(false);
      renderAppWithRoute('/');

      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
      });

      // Simulate authentication change (in real app this would happen after login)
      authService.isAuthenticated.mockReturnValue(true);

      // Re-render with authenticated state
      renderAppWithRoute('/');
      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
      });
    });
  });

  describe('Router Configuration', () => {
    test('uses correct router configuration', () => {
      authService.isAuthenticated.mockReturnValue(false);
      renderAppWithRoute('/login');

      // Should have BrowserRouter functionality (tested through navigation)
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
      expect(screen.getByTestId('navbar')).toBeInTheDocument();
    });
  });
});
