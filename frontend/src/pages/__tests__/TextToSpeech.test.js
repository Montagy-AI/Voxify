import React from 'react';
import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from '@testing-library/react';
import '@testing-library/jest-dom';
import TextToSpeech from '../TextToSpeech';

// Import mocked services
import voiceCloneService from '../../services/voiceClone.service';

// Mock the services
jest.mock('../../services/job.service', () => ({
  getSynthesisJobs: jest.fn(),
}));

jest.mock('../../services/voiceClone.service', () => ({
  listVoiceClones: jest.fn(),
  synthesizeWithClone: jest.fn(),
}));

jest.mock('../../config/api.config', () => ({
  apiBaseUrl: 'http://localhost:8000',
}));

// Mock window.alert
global.alert = jest.fn();

// Mock audio methods
Object.defineProperty(window.HTMLMediaElement.prototype, 'play', {
  writable: true,
  value: jest.fn().mockImplementation(() => Promise.resolve()),
});

Object.defineProperty(window.HTMLMediaElement.prototype, 'pause', {
  writable: true,
  value: jest.fn(),
});

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

// Mock URL methods
Object.defineProperty(window, 'URL', {
  value: {
    createObjectURL: jest.fn(() => 'mock-blob-url'),
    revokeObjectURL: jest.fn(),
  },
});

// Mock fetch
global.fetch = jest.fn();

// Setup and cleanup for each test
afterEach(() => {
  cleanup();
  jest.clearAllMocks();
});

describe('TextToSpeech Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.alert.mockClear();
    mockLocalStorage.getItem.mockReturnValue('mock-token');

    // Default mock for voice clones
    voiceCloneService.listVoiceClones.mockResolvedValue({
      success: true,
      data: {
        clones: [
          {
            clone_id: 'clone-1',
            name: 'John Voice',
            language: 'en-US',
            status: 'ready',
            created_at: '2024-01-15T10:00:00Z',
          },
          {
            clone_id: 'clone-2',
            name: 'Jane Voice',
            language: 'en-GB',
            status: 'processing',
            created_at: '2024-01-16T10:00:00Z',
          },
        ],
      },
    });
  });

  describe('Initial Render', () => {
    test('renders main heading and form elements', async () => {
      render(<TextToSpeech />);

      expect(screen.getByText('Text to Speech')).toBeInTheDocument();
      expect(screen.getByLabelText('Text')).toBeInTheDocument();
      expect(screen.getByLabelText('Select Voice Clone')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.getByText('Generate with Voice Clone')).toBeInTheDocument();
    });

    test('loads voice clones on mount', async () => {
      render(<TextToSpeech />);

      await waitFor(() => {
        expect(voiceCloneService.listVoiceClones).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(
          screen.getByText('Jane Voice (en-GB) - processing')
        ).toBeInTheDocument();
      });
    });

    test('shows loading state for voice clones initially', () => {
      voiceCloneService.listVoiceClones.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () => resolve({ success: true, data: { clones: [] } }),
              100
            )
          )
      );

      render(<TextToSpeech />);

      expect(screen.getByText('Loading voice clones...')).toBeInTheDocument();
    });

    test('submit button is initially disabled', () => {
      render(<TextToSpeech />);

      const submitButton = screen.getByText('Generate with Voice Clone');
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveClass('opacity-50', 'cursor-not-allowed');
    });
  });

  describe('Form Input Handling', () => {
    test('updates text input correctly', async () => {
      render(<TextToSpeech />);

      const textInput = screen.getByLabelText('Text');
      fireEvent.change(textInput, { target: { value: 'Hello world' } });

      expect(textInput).toHaveValue('Hello world');
    });

    test('updates voice selection correctly', async () => {
      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const voiceSelect = screen.getByLabelText('Select Voice Clone');
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      expect(voiceSelect).toHaveValue('clone-1');
    });

    test('updates language configuration correctly', () => {
      render(<TextToSpeech />);

      const languageSelect = screen.getByLabelText('Language');
      fireEvent.change(languageSelect, { target: { value: 'fr-FR' } });

      expect(languageSelect).toHaveValue('fr-FR');
    });
  });

  describe('Voice Clone Information Display', () => {
    test('shows selected voice clone information when voice is selected', async () => {
      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const voiceSelect = screen.getByLabelText('Select Voice Clone');
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      expect(screen.getByText('Selected Voice Clone')).toBeInTheDocument();
      expect(screen.getByText('John Voice')).toBeInTheDocument();
      expect(screen.getByText('en-US')).toBeInTheDocument();
      expect(screen.getByText('ready')).toBeInTheDocument();
    });

    test('does not show voice clone info when no voice is selected', async () => {
      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      expect(
        screen.queryByText('Selected Voice Clone')
      ).not.toBeInTheDocument();
    });

    test('shows status with correct styling for ready voice', async () => {
      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const voiceSelect = screen.getByLabelText('Select Voice Clone');
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const statusElement = screen.getByText('ready');
      expect(statusElement).toHaveClass('text-green-400');
    });
  });

  describe('Voice Clone Loading States', () => {
    test('handles empty voice clones list', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        success: true,
        data: { clones: [] },
      });

      render(<TextToSpeech />);

      await waitFor(() => {
        expect(
          screen.getByText(
            'No voice clones available. Create one in Voice Clone page.'
          )
        ).toBeInTheDocument();
      });
    });

    test('handles voice clone loading failure', async () => {
      const consoleSpy = jest
        .spyOn(console, 'error')
        .mockImplementation(() => {});
      voiceCloneService.listVoiceClones.mockRejectedValue(
        new Error('Network error')
      );

      render(<TextToSpeech />);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          'Failed to load voice clones:',
          expect.any(Error)
        );
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Form Validation', () => {
    test('prevents submission without text', async () => {
      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const voiceSelect = screen.getByLabelText('Select Voice Clone');
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      expect(submitButton).toBeDisabled();
    });

    test('prevents submission without voice selection', async () => {
      render(<TextToSpeech />);

      const textInput = screen.getByLabelText('Text');
      fireEvent.change(textInput, { target: { value: 'Hello world' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      expect(submitButton).toBeDisabled();
    });

    test('enables submission when all requirements are met', async () => {
      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      expect(submitButton).not.toBeDisabled();
      expect(submitButton).not.toHaveClass('opacity-50', 'cursor-not-allowed');
    });
  });

  describe('Speech Generation', () => {
    test('successful speech generation shows generated audio player', async () => {
      const mockSynthesizeResponse = {
        success: true,
        data: {
          job_id: 'job-123',
          output_path: '/path/to/audio.wav',
        },
      };
      voiceCloneService.synthesizeWithClone.mockResolvedValue(
        mockSynthesizeResponse
      );

      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(voiceCloneService.synthesizeWithClone).toHaveBeenCalledWith(
          'clone-1',
          'Hello world test',
          {
            language: 'en-US',
            outputFormat: 'wav',
            sampleRate: 22050,
          }
        );
      });

      await waitFor(() => {
        expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      });
    });

    test('handles speech generation failure', async () => {
      voiceCloneService.synthesizeWithClone.mockRejectedValue(
        new Error('Generation failed')
      );

      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(global.alert).toHaveBeenCalledWith(
          'Failed to generate speech: Generation failed'
        );
      });
    });
  });

  describe('Error Handling', () => {
    test('logs error when voice clone loading fails', async () => {
      const consoleSpy = jest
        .spyOn(console, 'error')
        .mockImplementation(() => {});
      voiceCloneService.listVoiceClones.mockRejectedValue(
        new Error('API Error')
      );

      render(<TextToSpeech />);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          'Failed to load voice clones:',
          expect.any(Error)
        );
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Configuration Controls', () => {
    test('updates speed configuration correctly', () => {
      render(<TextToSpeech />);

      const speedSelect = screen.getByLabelText('Speed');
      expect(speedSelect).toHaveValue('1.0');

      // Speed currently only has "Normal" option, but test the control exists
      expect(speedSelect).toBeInTheDocument();
    });

    test('updates pitch configuration correctly', () => {
      render(<TextToSpeech />);

      const pitchSelect = screen.getByLabelText('Pitch');
      expect(pitchSelect).toHaveValue('1.0');

      // Pitch currently only has "Normal" option, but test the control exists
      expect(pitchSelect).toBeInTheDocument();
    });

    test('updates volume configuration correctly', () => {
      render(<TextToSpeech />);

      const volumeSelect = screen.getByLabelText('Volume');
      expect(volumeSelect).toHaveValue('1.0');

      // Volume currently only has "Normal" option, but test the control exists
      expect(volumeSelect).toBeInTheDocument();
    });

    test('all settings controls are disabled during generation', async () => {
      const mockSynthesizeResponse = {
        success: true,
        data: { job_id: 'job-123', output_path: '/path/to/audio.wav' },
      };
      voiceCloneService.synthesizeWithClone.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve(mockSynthesizeResponse), 100)
          )
      );

      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      // Check that controls are disabled during generation
      expect(screen.getByLabelText('Text')).toBeDisabled();
      expect(screen.getByLabelText('Select Voice Clone')).toBeDisabled();
      expect(screen.getByLabelText('Language')).toBeDisabled();
      expect(screen.getByLabelText('Speed')).toBeDisabled();
      expect(screen.getByLabelText('Pitch')).toBeDisabled();
      expect(screen.getByLabelText('Volume')).toBeDisabled();
    });
  });

  describe('Progress Indication', () => {
    test('shows progress bar during generation', async () => {
      const mockSynthesizeResponse = {
        success: true,
        data: { job_id: 'job-123', output_path: '/path/to/audio.wav' },
      };
      voiceCloneService.synthesizeWithClone.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve(mockSynthesizeResponse), 100)
          )
      );

      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      // Check progress elements appear
      expect(screen.getByText('Generating')).toBeInTheDocument();
      expect(screen.getByText(/% complete/)).toBeInTheDocument();

      // Check button text changes
      expect(screen.getByText('Generating...')).toBeInTheDocument();
    });
  });

  describe('Generated Audio Player', () => {
    beforeEach(async () => {
      const mockSynthesizeResponse = {
        success: true,
        data: { job_id: 'job-123', output_path: '/path/to/audio.wav' },
      };
      voiceCloneService.synthesizeWithClone.mockResolvedValue(
        mockSynthesizeResponse
      );

      // Mock successful audio fetch
      global.fetch.mockResolvedValue({
        ok: true,
        blob: () =>
          Promise.resolve(new Blob(['audio-data'], { type: 'audio/wav' })),
      });
    });

    test('displays generated audio information correctly', async () => {
      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      });

      expect(screen.getByText('Voice Clone')).toBeInTheDocument();
      expect(screen.getAllByText('John Voice')[1]).toBeInTheDocument();
      expect(screen.getAllByText('en-US')[1]).toBeInTheDocument();
      expect(screen.getAllByText('Hello world test')[1]).toBeInTheDocument();
    });

    test('truncates long text in audio information display', async () => {
      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const longText =
        'This is a very long text that should be truncated when displayed in the audio information section because it exceeds 100 characters in length.';

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: longText } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      });

      // Check that text is truncated
      expect(
        screen.getByText(/This is a very long text.*\.\.\./)
      ).toBeInTheDocument();
    });

    test('play button exists and is clickable', async () => {
      render(<TextToSpeech />);

      // Generate audio first
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      });

      const playButton = screen.getByRole('button', { name: '▶️ Play' });
      expect(playButton).toBeInTheDocument();
      expect(playButton).not.toBeDisabled();
    });

    test('download button exists and is clickable', async () => {
      render(<TextToSpeech />);

      // Generate audio first
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      });

      const downloadButton = screen.getByRole('button', { name: '⬇️ Download' });
      expect(downloadButton).toBeInTheDocument();
      expect(downloadButton).not.toBeDisabled();
    });

    test('new generation button functionality', async () => {
      render(<TextToSpeech />);

      // Generate audio first
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      });

      const newGenerationButton = screen.getByRole('button', { name: '🔄 Generate New' });
      fireEvent.click(newGenerationButton);

      // Check that form is reset
      expect(screen.queryByText('Generated Audio')).not.toBeInTheDocument();
      expect(screen.getByLabelText('Text')).toHaveValue('');
      expect(screen.getByLabelText('Select Voice Clone')).toHaveValue('');
    });
  });

  describe('Audio Error Handling', () => {
    test('audio player renders correctly with controls', async () => {
      const mockSynthesizeResponse = {
        success: true,
        data: { job_id: 'job-123', output_path: '/path/to/audio.wav' },
      };
      voiceCloneService.synthesizeWithClone.mockResolvedValue(
        mockSynthesizeResponse
      );

      render(<TextToSpeech />);

      // Generate audio first
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      });

      // Check that audio controls are present
      expect(screen.getByText('Play')).toBeInTheDocument();
      expect(screen.getByText('Download')).toBeInTheDocument();
      expect(screen.getByText('Generate New')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('handles empty voice clones response gracefully', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        success: true,
        data: { clones: null }, // null instead of empty array
      });

      render(<TextToSpeech />);

      await waitFor(() => {
        expect(
          screen.getByText(
            'No voice clones available. Create one in Voice Clone page.'
          )
        ).toBeInTheDocument();
      });
    });

    test('handles synthesis response without data gracefully', async () => {
      voiceCloneService.synthesizeWithClone.mockResolvedValue({
        success: true,
        data: null, // No data in response
      });

      render(<TextToSpeech />);

      // Wait for voice clones to load
      await waitFor(() => {
        expect(
          screen.getByText('John Voice (en-US) - ready')
        ).toBeInTheDocument();
      });

      const textInput = screen.getByLabelText('Text');
      const voiceSelect = screen.getByLabelText('Select Voice Clone');

      fireEvent.change(textInput, { target: { value: 'Hello world test' } });
      fireEvent.change(voiceSelect, { target: { value: 'clone-1' } });

      const submitButton = screen.getByText('Generate with Voice Clone');
      fireEvent.click(submitButton);

      // Should handle gracefully and still show generated audio section
      await waitFor(() => {
        expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      });
    });

    test('component renders without errors when no generated audio exists', () => {
      render(<TextToSpeech />);

      // Component should render without generated audio section
      expect(screen.getByText('Text to Speech')).toBeInTheDocument();
      expect(screen.queryByText('Generated Audio')).not.toBeInTheDocument();
    });

    test('handles voice clone with missing name gracefully', async () => {
      voiceCloneService.listVoiceClones.mockResolvedValue({
        success: true,
        data: {
          clones: [
            {
              clone_id: 'clone-1',
              name: null, // Missing name
              language: 'en-US',
              status: 'ready',
              created_at: '2024-01-15T10:00:00Z',
            },
          ],
        },
      });

      render(<TextToSpeech />);

      await waitFor(() => {
        // Should still load and display options despite missing name
        expect(screen.getByLabelText('Select Voice Clone')).toBeInTheDocument();
      });
    });

    test('component handles all required settings', () => {
      render(<TextToSpeech />);

      // Verify all settings controls are present
      expect(screen.getByLabelText('Language')).toBeInTheDocument();
      expect(screen.getByLabelText('Speed')).toBeInTheDocument();
      expect(screen.getByLabelText('Pitch')).toBeInTheDocument();
      expect(screen.getByLabelText('Volume')).toBeInTheDocument();

      // Verify default values
      expect(screen.getByLabelText('Language')).toHaveValue('en-US');
      expect(screen.getByLabelText('Speed')).toHaveValue('1.0');
      expect(screen.getByLabelText('Pitch')).toHaveValue('1.0');
      expect(screen.getByLabelText('Volume')).toHaveValue('1.0');
    });
  });
});
