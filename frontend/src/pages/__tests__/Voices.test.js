import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Voices from '../Voices';

// Mock the auth service
jest.mock('../../services/auth.service', () => ({
  getCurrentUser: jest.fn(),
  isAuthenticated: jest.fn(),
}));

// Mock the API config
jest.mock('../../config/api.config', () => ({
  apiBaseUrl: 'http://localhost:3000/api',
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

// Mock fetch
global.fetch = jest.fn();

describe('Voices Component', () => {
  const mockVoiceClones = [
    {
      clone_id: '1',
      name: 'Test Voice 1',
      description: 'A test voice clone',
      language: 'en-US',
      status: 'completed',
      created_at: '2025-01-15T10:30:00Z',
    },
    {
      clone_id: '2',
      name: 'Test Voice 2',
      description: 'Another test voice clone',
      language: 'zh-CN',
      status: 'training',
      created_at: '2025-01-14T15:45:00Z',
    },
    {
      clone_id: '3',
      name: 'Failed Voice',
      description: 'A failed voice clone',
      language: 'es-ES',
      status: 'failed',
      created_at: '2025-01-13T09:15:00Z',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue('mock-token');
    authService.getCurrentUser.mockReturnValue({ id: 1, email: 'test@test.com' });
    authService.isAuthenticated.mockReturnValue(true);
    // Mock console.error to avoid noise in tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  /*
   * Authentication Tests
   */
  describe('Authentication', () => {
    test('redirects to login when user is not authenticated', async () => {
      authService.getCurrentUser.mockReturnValue(null);
      authService.isAuthenticated.mockReturnValue(false);

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });

    test('redirects to login when no access token in localStorage', async () => {
      mockLocalStorage.getItem.mockReturnValue(null);

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });

    test('redirects to login when user exists but is not authenticated', async () => {
      authService.getCurrentUser.mockReturnValue({ id: 1, email: 'test@test.com' });
      authService.isAuthenticated.mockReturnValue(false);

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });
  });

  /*
   * Loading State Tests
   */
  describe('Loading State', () => {
    test('shows loading spinner initially', () => {
      // Mock slow API response
      fetch.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({ success: true, data: { clones: [] } })
        }), 100))
      );

      renderWithRouter(<Voices />);

      expect(screen.getByText('Voice Clones')).toBeInTheDocument();
      expect(document.querySelector('.animate-spin')).toBeInTheDocument();
    });

    test('hides loading spinner after data is loaded', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).not.toBeInTheDocument();
      });
    });
  });

  /*
   * API Call Tests
   */
  describe('API Calls', () => {
    test('makes correct API call with authorization header', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          'http://localhost:3000/api/voice/clones',
          {
            headers: {
              Authorization: 'Bearer mock-token',
            },
          }
        );
      });
    });

    test('handles successful API response with voice clones', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('Test Voice 1')).toBeInTheDocument();
        expect(screen.getByText('Test Voice 2')).toBeInTheDocument();
        expect(screen.getByText('Failed Voice')).toBeInTheDocument();
      });
    });

    test('handles API response with no clones', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: [] } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('No voice clones found')).toBeInTheDocument();
        expect(screen.getByText('You can create your first voice clone using the Dashboard')).toBeInTheDocument();
      });
    });
  });

  /*
   * Error Handling Tests
   */
  describe('Error Handling', () => {
    test('displays error when API response is not ok', async () => {
      fetch.mockResolvedValue({
        ok: false,
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('Failed to fetch voice clones')).toBeInTheDocument();
      });
    });

    test('displays error when API returns success: false', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: false, error: 'Custom API error' })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('Custom API error')).toBeInTheDocument();
      });
    });

    test('displays generic error when API returns success: false without error message', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: false })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('Unknown error')).toBeInTheDocument();
      });
    });

    test('handles network errors', async () => {
      fetch.mockRejectedValue(new Error('Network error'));

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });
  });

  /*
   * Voice Clone Display Tests
   */
  describe('Voice Clone Display', () => {
    beforeEach(() => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });
    });

    test('displays voice clone information correctly', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        // Check first voice clone
        expect(screen.getByText('Test Voice 1')).toBeInTheDocument();
        expect(screen.getByText('A test voice clone')).toBeInTheDocument();
        expect(screen.getByText('en-US')).toBeInTheDocument();
        expect(screen.getByText('Ready')).toBeInTheDocument();
      });
    });

    test('displays default values for missing fields', async () => {
      const cloneWithMissingFields = [{
        clone_id: '1',
        status: 'completed',
        created_at: '2025-01-15T10:30:00Z',
      }];

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: cloneWithMissingFields } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('Unnamed Voice')).toBeInTheDocument();
        expect(screen.getByText('No description provided.')).toBeInTheDocument();
        expect(screen.getByText('zh-CN')).toBeInTheDocument(); // Default language
      });
    });

    test('formats creation date correctly', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        // Check that date is formatted (actual format from component)
        // The component shows "Created: Jan 15, 2025, 10:30 AM" format (UTC to local time conversion)
        expect(screen.getByText(/Created:\s*Jan.*15.*2025.*10:30.*AM/)).toBeInTheDocument();
      });
    });
  });

  /*
   * Status Display Tests
   */
  describe('Status Display', () => {
    beforeEach(() => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });
    });

    test('displays correct status colors and text', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        // Check completed status shows as "Ready"
        const readyStatus = screen.getByText('Ready');
        expect(readyStatus).toBeInTheDocument();
        expect(readyStatus).toHaveClass('text-green-500');

        // Check training status
        const trainingStatus = screen.getByText('training');
        expect(trainingStatus).toBeInTheDocument();
        expect(trainingStatus).toHaveClass('text-yellow-500');

        // Check failed status
        const failedStatus = screen.getByText('failed');
        expect(failedStatus).toBeInTheDocument();
        expect(failedStatus).toHaveClass('text-red-500');
      });
    });

    test('handles unknown status with default styling', async () => {
      const cloneWithUnknownStatus = [{
        clone_id: '1',
        name: 'Test Voice',
        status: 'unknown_status',
        created_at: '2025-01-15T10:30:00Z',
      }];

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: cloneWithUnknownStatus } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        const unknownStatus = screen.getByText('unknown_status');
        expect(unknownStatus).toBeInTheDocument();
        expect(unknownStatus).toHaveClass('text-gray-400');
      });
    });

    test('handles null/undefined status', async () => {
      const cloneWithNullStatus = [{
        clone_id: '1',
        name: 'Test Voice',
        status: null,
        created_at: '2025-01-15T10:30:00Z',
      }];

      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: cloneWithNullStatus } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        // Should handle null status gracefully
        expect(screen.getByText('Test Voice')).toBeInTheDocument();
      });
    });
  });

  /*
   * Navigation Tests
   */
  describe('Navigation', () => {
    beforeEach(() => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });
    });

    test('navigates to text-to-speech when completed voice clone is clicked', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        const voiceCloneCard = screen.getByText('Test Voice 1').closest('div.group');
        expect(voiceCloneCard).toBeInTheDocument();
      });

      const voiceCloneCard = screen.getByText('Test Voice 1').closest('div.group');
      fireEvent.click(voiceCloneCard);

      expect(mockNavigate).toHaveBeenCalledWith('/tasks/text-to-speech/');
    });

    test('navigates to text-to-speech when any voice clone is clicked', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        const trainingVoiceCard = screen.getByText('Test Voice 2').closest('div.group');
        expect(trainingVoiceCard).toBeInTheDocument();
      });

      const trainingVoiceCard = screen.getByText('Test Voice 2').closest('div.group');
      fireEvent.click(trainingVoiceCard);

      expect(mockNavigate).toHaveBeenCalledWith('/tasks/text-to-speech/');
    });
  });

  /*
   * UI State Tests
   */
  describe('UI States', () => {
    test('shows empty state with illustration when no clones exist', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: [] } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('No voice clones found')).toBeInTheDocument();
        expect(screen.getByText('You can create your first voice clone using the Dashboard')).toBeInTheDocument();
        
        // Check for SVG icon
        const svgIcon = document.querySelector('svg');
        expect(svgIcon).toBeInTheDocument();
        expect(svgIcon).toHaveClass('h-12', 'w-12', 'text-gray-400');
      });
    });

    test('shows error state with proper styling', async () => {
      fetch.mockResolvedValue({
        ok: false,
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        const errorElement = screen.getByText('Failed to fetch voice clones');
        expect(errorElement).toBeInTheDocument();
        expect(errorElement.closest('div')).toHaveClass('text-red-500', 'text-center', 'bg-red-500/10');
      });
    });

    test('applies hover effects to voice clone cards', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        const voiceCloneCard = screen.getByText('Test Voice 1').closest('div.group');
        expect(voiceCloneCard).toHaveClass('hover:bg-zinc-800', 'transition-colors', 'cursor-pointer');
      });
    });
  });

  /*
   * Arrow Icon Tests
   */
  describe('Arrow Icon States', () => {
    beforeEach(() => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });
    });

    test('shows active arrow for completed voice clones', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        const completedVoiceCard = screen.getByText('Test Voice 1').closest('div.group');
        const arrow = completedVoiceCard.querySelector('svg');
        expect(arrow).toHaveClass('text-white');
        expect(arrow).not.toHaveClass('text-zinc-500');
      });
    });

    test('shows inactive arrow for non-completed voice clones', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        const trainingVoiceCard = screen.getByText('Test Voice 2').closest('div.group');
        const arrow = trainingVoiceCard.querySelector('svg');
        expect(arrow).toHaveClass('text-zinc-500');
        expect(arrow).not.toHaveClass('text-white');
      });
    });
  });

  /*
   * Component Integration Tests
   */
  describe('Component Integration', () => {
    test('handles multiple re-renders correctly', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });

      const { rerender } = renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('Test Voice 1')).toBeInTheDocument();
      });

      // Re-render component
      rerender(<BrowserRouter><Voices /></BrowserRouter>);

      await waitFor(() => {
        expect(screen.getByText('Test Voice 1')).toBeInTheDocument();
      });
    });

    test('handles error state correctly and shows proper error message', async () => {
      fetch.mockResolvedValue({
        ok: false,
      });

      renderWithRouter(<Voices />);

      await waitFor(() => {
        expect(screen.getByText('Failed to fetch voice clones')).toBeInTheDocument();
      });

      // Verify error styling is applied
      const errorElement = screen.getByText('Failed to fetch voice clones');
      expect(errorElement.closest('div')).toHaveClass('text-red-500', 'text-center', 'bg-red-500/10');
    });
  });

  /*
   * Accessibility Tests
   */
  describe('Accessibility', () => {
    beforeEach(() => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { clones: mockVoiceClones } })
      });
    });

    test('voice clone cards are clickable and have proper structure', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        const voiceCloneCards = screen.getAllByRole('button');
        expect(voiceCloneCards.length).toBeGreaterThan(0);
      });
    });

    test('page has proper heading structure', async () => {
      renderWithRouter(<Voices />);

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Voice Clones');
    });

    test('voice clone names are properly displayed as headings', async () => {
      renderWithRouter(<Voices />);

      await waitFor(() => {
        const voiceNames = screen.getAllByRole('heading', { level: 3 });
        expect(voiceNames.length).toBe(3);
        expect(voiceNames[0]).toHaveTextContent('Test Voice 1');
        expect(voiceNames[1]).toHaveTextContent('Test Voice 2');
        expect(voiceNames[2]).toHaveTextContent('Failed Voice');
      });
    });
  });
});
