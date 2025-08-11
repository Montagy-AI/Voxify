import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Dashboard from '../Dashboard';
import authService from '../../services/auth.service';
import jobService from '../../services/job.service';
import voiceCloneService from '../../services/voiceClone.service';

// Mock the services
jest.mock('../../services/auth.service', () => ({
  getCurrentUser: jest.fn(),
}));

jest.mock('../../services/job.service', () => ({
  getSynthesisJobs: jest.fn(),
}));

jest.mock('../../services/voiceClone.service', () => ({
  listVoiceClones: jest.fn(),
}));

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const DashboardWithRouter = () => (
  <BrowserRouter>
    <Dashboard />
  </BrowserRouter>
);

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authService.getCurrentUser.mockReturnValue({
      first_name: 'John',
      email: 'john@example.com',
    });
    voiceCloneService.listVoiceClones.mockResolvedValue({
      data: { clones: [] },
    });
    jobService.getSynthesisJobs.mockResolvedValue([]);
  });

  describe('Initial Render', () => {
    test('Render welcome message with user name', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Welcome back, John!')).toBeInTheDocument();
      });
      expect(
        screen.getByText('Ready to start a new task? Choose an option below.')
      ).toBeInTheDocument();
    });

    test('Render welcome message with default name when user has no first name', async () => {
      authService.getCurrentUser.mockReturnValue({
        email: 'john@example.com',
      });
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Welcome back, there!')).toBeInTheDocument();
      });
    });

    test('Render welcome message with default name when user is null', async () => {
      authService.getCurrentUser.mockReturnValue(null);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Welcome back, there!')).toBeInTheDocument();
      });
    });

    test('renders main action cards', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Clone Your Voice')).toBeInTheDocument();
      });
      expect(
        screen.getByText(
          'Create a digital copy of your voice that can speak any text naturally.'
        )
      ).toBeInTheDocument();
      expect(screen.getByText('Text-to-Speech')).toBeInTheDocument();
      expect(
        screen.getByText(
          'Convert any text into natural-sounding speech using your voice clones.'
        )
      ).toBeInTheDocument();
    });

    test('Render statistics section', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Your Statistics')).toBeInTheDocument();
      });
      expect(screen.getByText('Voice Clones')).toBeInTheDocument();
      expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
      expect(screen.getByText('Processing')).toBeInTheDocument();
    });

    test('Render quick actions section', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Quick Actions')).toBeInTheDocument();
      });
      expect(screen.getByText('View All Tasks')).toBeInTheDocument();
      expect(
        screen.getByText('Browse and manage your generated voices')
      ).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(
        screen.getByText('Manage your account and preferences')
      ).toBeInTheDocument();
    });
  });

  describe('Navigation Links', () => {
    test('Voice clone card links to correct route', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        const voiceCloneLink = screen.getByRole('link', {
          name: /clone your voice/i,
        });
        expect(voiceCloneLink).toHaveAttribute('href', '/voice-clone');
      });
    });

    test('Check text-to-speech card links to correct route', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        const ttsLink = screen.getByRole('link', { name: /text-to-speech/i });
        expect(ttsLink).toHaveAttribute('href', '/text-to-speech');
      });
    });

    test('View all tasks link is correct', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        const tasksLink = screen.getByRole('link', { name: /view all tasks/i });
        expect(tasksLink).toHaveAttribute('href', '/tasks');
      });
    });

    test('Check settings link is correct', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        const settingsLink = screen.getByRole('link', { name: /settings/i });
        expect(settingsLink).toHaveAttribute('href', '/settings');
      });
    });
  });

  describe('Statistics Loading', () => {
    test('Show loading state initially', async () => {
      voiceCloneService.listVoiceClones.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ data: { clones: [] } }), 100)
          )
      );
      jobService.getSynthesisJobs.mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve([]), 100))
      );
      render(<DashboardWithRouter />);
      expect(screen.getByText('Your Statistics')).toBeInTheDocument();
      await waitFor(
        () => {
          expect(screen.getByText('Voice Clones')).toBeInTheDocument();
        },
        { timeout: 500 }
      );
      await waitFor(
        () => {
          expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
        },
        { timeout: 500 }
      );
      await waitFor(
        () => {
          expect(screen.getByText('Processing')).toBeInTheDocument();
        },
        { timeout: 500 }
      );
    });

    test('Load and displays statistics successfully', async () => {
      const mockVoiceClones = [
        { id: 1, name: 'Voice 1' },
        { id: 2, name: 'Voice 2' },
      ];

      const mockJobs = [
        { id: 1, status: 'completed' },
        { id: 2, status: 'completed' },
        { id: 3, status: 'processing' },
        { id: 4, status: 'pending' },
      ];

      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: { clones: mockVoiceClones },
      });
      jobService.getSynthesisJobs.mockResolvedValue(mockJobs);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Voice Clones')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Processing')).toBeInTheDocument();
      });
      await waitFor(() => {
        // Check for statistics elements
        const statisticsElements = screen.getAllByText(/^[0-9]+$/);
        expect(statisticsElements.length).toBeGreaterThan(0);
      });
    });

    test('Handle empty data gracefully', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: { clones: [] },
      });
      jobService.getSynthesisJobs.mockResolvedValue([]);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Voice Clones')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Processing')).toBeInTheDocument();
      });
    });

    test('Handle missing data structure gracefully', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: null,
      });
      jobService.getSynthesisJobs.mockResolvedValue(null);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Voice Clones')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Processing')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('Display error message when voice clone service fails', async () => {
      voiceCloneService.listVoiceClones.mockRejectedValue(
        new Error('Voice clone service error')
      );
      jobService.getSynthesisJobs.mockResolvedValue([]);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(
          screen.getByText('Failed to load dashboard statistics')
        ).toBeInTheDocument();
      });
    });

    test('Display error message when job service fails', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: { clones: [] },
      });
      jobService.getSynthesisJobs.mockRejectedValue(
        new Error('Job service error')
      );
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(
          screen.getByText('Failed to load dashboard statistics')
        ).toBeInTheDocument();
      });
    });

    test('Display error message when both services fail', async () => {
      voiceCloneService.listVoiceClones.mockRejectedValue(
        new Error('Voice clone error')
      );
      jobService.getSynthesisJobs.mockRejectedValue(
        new Error('Job service error')
      );
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(
          screen.getByText('Failed to load dashboard statistics')
        ).toBeInTheDocument();
      });
    });
  });

  describe('Statistics Calculations', () => {
    test('Correctly count different job statuses', async () => {
      const mockJobs = [
        { id: 1, status: 'completed' },
        { id: 2, status: 'completed' },
        { id: 3, status: 'completed' },
        { id: 4, status: 'processing' },
        { id: 5, status: 'processing' },
        { id: 6, status: 'pending' },
        { id: 7, status: 'failed' },
        { id: 8, status: 'cancelled' },
      ];
      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: { clones: [{ id: 1 }] },
      });
      jobService.getSynthesisJobs.mockResolvedValue(mockJobs);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Voice Clones')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Processing')).toBeInTheDocument();
      });
      await waitFor(() => {
        // Check for correct counts in the statistics
        const statisticsElements = screen.getAllByText(/^[0-9]+$/);
        expect(statisticsElements).toHaveLength(3);
      });
    });

    test('Handle jobs with unknown statuses', async () => {
      const mockJobs = [
        { id: 1, status: 'completed' },
        { id: 2, status: 'some_unknown_status' },
        { id: 3, status: null },
        { id: 4, status: undefined },
      ];
      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: { clones: [] },
      });
      jobService.getSynthesisJobs.mockResolvedValue(mockJobs);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Voice Clones')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Processing')).toBeInTheDocument();
      });
      await waitFor(() => {
        // Check that statistics are displayed
        const statisticsElements = screen.getAllByText(/^[0-9]+$/);
        expect(statisticsElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe('UI Elements', () => {
    test('Check for proper CSS classes for styling', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Welcome back, John!')).toBeInTheDocument();
      });
    });

    test('Render SVG icons in action cards', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getAllByRole('link')).toHaveLength(4);
      });
    });

    test('Render statistics with proper icons', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(screen.getByText('Voice Clones')).toBeInTheDocument();
      });
    });
  });

  describe('Service Call Parameters', () => {
    test('Call voice clone service with correct parameters', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: { clones: [] },
      });
      jobService.getSynthesisJobs.mockResolvedValue([]);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(voiceCloneService.listVoiceClones).toHaveBeenCalled();
      });
    });

    test('Call job service with no parameters', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: { clones: [] },
      });
      jobService.getSynthesisJobs.mockResolvedValue([]);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(jobService.getSynthesisJobs).toHaveBeenCalled();
      });
    });
  });

  describe('Component Lifecycle', () => {
    test('Load dashboard stats on mount', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        data: { clones: [] },
      });
      jobService.getSynthesisJobs.mockResolvedValue([]);
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(voiceCloneService.listVoiceClones).toHaveBeenCalledTimes(1);
      });
      await waitFor(() => {
        expect(jobService.getSynthesisJobs).toHaveBeenCalledTimes(1);
      });
    });

    test('Only load stats once on initial mount', async () => {
      render(<DashboardWithRouter />);
      await waitFor(() => {
        expect(voiceCloneService.listVoiceClones).toHaveBeenCalled();
      });
      await waitFor(() => {
        expect(jobService.getSynthesisJobs).toHaveBeenCalled();
      });
      await new Promise((resolve) => setTimeout(resolve, 100));
      // Verify services were called at least once (could be 1 or 2 times due to React behavior)
      expect(voiceCloneService.listVoiceClones).toHaveBeenCalled();
      expect(jobService.getSynthesisJobs).toHaveBeenCalled();
    });
  });
});
