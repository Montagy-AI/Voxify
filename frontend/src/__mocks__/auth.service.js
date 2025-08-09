import { render, screen, waitFor, cleanup } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Tasks from './Tasks';

// Import mocked services
import jobService from './services/job.service';
import authService from './auth.service';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock the services
jest.mock('../services/job.service', () => ({
  getSynthesisJobs: jest.fn(),
  cancelSynthesisJob: jest.fn(),
}));

jest.mock('../services/auth.service', () => ({
  getCurrentUser: jest.fn(),
  isAuthenticated: jest.fn(),
  refreshToken: jest.fn(),
}));

jest.mock('../config/api.config', () => ({
  apiBaseUrl: 'http://localhost:8000',
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Helper component to wrap Tasks with Router
const TasksWithRouter = () => (
  <BrowserRouter>
    <Tasks />
  </BrowserRouter>
);

// Setup and cleanup for each test
afterEach(() => {
  cleanup();
  jest.clearAllMocks();
});

describe('Tasks Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue('mock-token');

    // Default authentication mocks
    authService.getCurrentUser.mockReturnValue({
      id: 1,
      email: 'test@example.com',
    });
    authService.isAuthenticated.mockReturnValue(true);
    authService.refreshToken.mockResolvedValue({ success: true });

    // Default jobs mock
    jobService.getSynthesisJobs.mockResolvedValue([]);
  });

  describe('Initial Render and Authentication', () => {
    test('renders main heading', async () => {
      render(<TasksWithRouter />);

      expect(screen.getByText('Generated Audio Files')).toBeInTheDocument();
    });

    test('redirects to login when user is not authenticated', async () => {
      authService.getCurrentUser.mockReturnValue(null);
      mockLocalStorage.getItem.mockReturnValue(null);

      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });

    test('shows loading state initially', () => {
      jobService.getSynthesisJobs.mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve([]), 100))
      );

      render(<TasksWithRouter />);

      // Check for loading spinner by class
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Jobs Loading and Display', () => {
    test('loads jobs on mount', async () => {
      const mockJobs = [
        {
          id: 'job-1',
          status: 'completed',
          text_content: 'Hello world',
          created_at: '2024-01-15T10:00:00Z',
          voice_model: { name: 'Test Voice' },
        },
      ];
      jobService.getSynthesisJobs.mockResolvedValue(mockJobs);

      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(jobService.getSynthesisJobs).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText('Hello world')).toBeInTheDocument();
      });
    });

    test('displays empty state when no jobs exist', async () => {
      jobService.getSynthesisJobs.mockResolvedValue([]);

      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(
          screen.getByText('No generated voices found')
        ).toBeInTheDocument();
      });
    });

    test('handles job loading failure with general error', async () => {
      jobService.getSynthesisJobs.mockRejectedValue(new Error('Network error'));

      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(
          screen.getByText(
            'Failed to load synthesis jobs. Please try again later.'
          )
        ).toBeInTheDocument();
      });
    });
  });

  describe('Job Status Display', () => {
    test('displays correct status colors', async () => {
      const mockJobs = [
        {
          id: 'job-1',
          status: 'completed',
          text_content: 'Completed job',
          created_at: '2024-01-15T10:00:00Z',
        },
      ];
      jobService.getSynthesisJobs.mockResolvedValue(mockJobs);

      render(<TasksWithRouter />);

      await waitFor(() => {
        const completedStatus = screen.getByText('Completed');
        expect(completedStatus).toHaveClass('text-green-500');
      });
    });

    test('identifies voice clone jobs correctly', async () => {
      const mockJobs = [
        {
          id: 'job-1',
          status: 'completed',
          text_content: 'Voice clone job',
          created_at: '2024-01-15T10:00:00Z',
          voice_model: { type: 'f5_tts' },
        },
      ];
      jobService.getSynthesisJobs.mockResolvedValue(mockJobs);

      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(screen.getByText('Voice Clone')).toBeInTheDocument();
      });
    });

    test('displays error message for failed jobs', async () => {
      const mockJobs = [
        {
          id: 'job-1',
          status: 'failed',
          text_content: 'Failed job',
          created_at: '2024-01-15T10:00:00Z',
          error_message: 'Something went wrong',
        },
      ];
      jobService.getSynthesisJobs.mockResolvedValue(mockJobs);

      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(
          screen.getByText('Error: Something went wrong')
        ).toBeInTheDocument();
      });
    });
  });

  describe('Service Integration', () => {
    test('calls authentication services correctly', async () => {
      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(authService.getCurrentUser).toHaveBeenCalled();
      });
    });

    test('handles authentication token refresh', async () => {
      authService.isAuthenticated.mockReturnValue(false);
      authService.refreshToken.mockResolvedValue({ success: true });

      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(authService.refreshToken).toHaveBeenCalled();
      });
    });

    test('redirects when token refresh fails', async () => {
      authService.isAuthenticated.mockReturnValue(false);
      authService.refreshToken.mockResolvedValue({ success: false });

      render(<TasksWithRouter />);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });
  });
});
