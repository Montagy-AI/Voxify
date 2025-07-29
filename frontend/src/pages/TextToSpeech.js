import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TextToSpeech from './TextToSpeech';

// Mock the services
jest.mock('../services/job.service', () => ({
	createSynthesisJob: jest.fn(),
}));

jest.mock('../services/voiceClone.service', () => ({
	listVoiceClones: jest.fn(),
	synthesizeWithClone: jest.fn(),
}));

// Mock apiConfig
jest.mock('../config/api.config', () => ({
	apiBaseUrl: 'https://api.example.com',
}));

// Import the mocked services
import jobService from '../services/job.service';
import voiceCloneService from '../services/voiceClone.service';

// Mock localStorage
const localStorageMock = {
	getItem: jest.fn(),
	setItem: jest.fn(),
	removeItem: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
	value: localStorageMock,
});

// Mock URL methods
global.URL.createObjectURL = jest.fn(() => 'mock-url');
global.URL.revokeObjectURL = jest.fn();

// Mock fetch
global.fetch = jest.fn();

// Mock audio methods
const mockAudio = {
	play: jest.fn().mockResolvedValue(undefined),
	pause: jest.fn(),
	load: jest.fn(),
	addEventListener: jest.fn(),
	removeEventListener: jest.fn(),
	src: '',
};

// Mock HTMLAudioElement
global.HTMLAudioElement = jest.fn(() => mockAudio);

// Mock document methods for download
const mockLink = {
	href: '',
	download: '',
	click: jest.fn(),
	setAttribute: jest.fn(),
	getAttribute: jest.fn(),
};

const mockDiv = {
	setAttribute: jest.fn(),
	getAttribute: jest.fn(),
	appendChild: jest.fn(),
	removeChild: jest.fn(),
	id: '',
};

// Fix the document.createElement mock
const originalCreateElement = document.createElement;
global.document.createElement = jest.fn((tagName) => {
	if (tagName === 'a') {
		return mockLink;
	}
	if (tagName === 'div') {
		return mockDiv;
	}
	// For other elements, use the original createElement or return a basic mock
	return originalCreateElement.call(document, tagName);
});

global.document.body.appendChild = jest.fn();
global.document.body.removeChild = jest.fn();
global.document.getElementById = jest.fn();

// Setup test environment before each test
beforeEach(() => {
	// Reset the mock div
	mockDiv.id = '';
	mockDiv.setAttribute.mockClear();
	
	// Mock getElementById to return our mock div when looking for 'root'
	global.document.getElementById.mockImplementation((id) => {
		if (id === 'root') {
			return { ...mockDiv, id: 'root' };
		}
		return null;
	});
});

afterEach(() => {
	// Clean up mocks
	jest.clearAllMocks();
});

describe('TextToSpeech Component', () => {
	beforeEach(() => {
		jest.clearAllMocks();
		localStorageMock.getItem.mockReturnValue('mock_token');
		
		// Mock successful voice clones response
		voiceCloneService.listVoiceClones.mockResolvedValue({
			success: true,
			data: {
				clones: [
					{
						clone_id: 'clone1',
						name: 'Test Voice 1',
						language: 'en-US',
						status: 'ready',
						created_at: '2023-01-01T00:00:00Z',
					},
					{
						clone_id: 'clone2',
						name: 'Test Voice 2',
						language: 'en-GB',
						status: 'processing',
						created_at: '2023-01-02T00:00:00Z',
					},
				],
			},
		});
	});

	describe('Initial Render', () => {
		test('renders text-to-speech form', async () => {
			render(<TextToSpeech />);

			expect(screen.getByText('Text to Speech')).toBeInTheDocument();
			expect(screen.getByLabelText('Text')).toBeInTheDocument();
			expect(screen.getByLabelText('Voice Type')).toBeInTheDocument();
			expect(screen.getByText('Voice Clones')).toBeInTheDocument();
			expect(screen.getByText('System Voices')).toBeInTheDocument();
		});

		test('loads voice clones on mount', async () => {
			render(<TextToSpeech />);

			await waitFor(() => {
				expect(voiceCloneService.listVoiceClones).toHaveBeenCalled();
			});

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
				expect(screen.getByText('Test Voice 2 (en-GB) - processing')).toBeInTheDocument();
			});
		});

		test('shows loading state while fetching voice clones', async () => {
			// Mock slow response
			voiceCloneService.listVoiceClones.mockImplementation(() => 
				new Promise(resolve => setTimeout(() => resolve({ success: true, data: { clones: [] } }), 100))
			);

			render(<TextToSpeech />);

			expect(screen.getByText('Loading voice clones...')).toBeInTheDocument();

			await waitFor(() => {
				expect(screen.queryByText('Loading voice clones...')).not.toBeInTheDocument();
			});
		});

		test('handles voice clones loading error', async () => {
			const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
			voiceCloneService.listVoiceClones.mockRejectedValue(new Error('Failed to load'));

			render(<TextToSpeech />);

			await waitFor(() => {
				expect(consoleSpy).toHaveBeenCalledWith('Failed to load voice clones:', expect.any(Error));
			});

			consoleSpy.mockRestore();
		});
	});

	describe('Form Interactions', () => {
		test('updates text input when typing', () => {
			render(<TextToSpeech />);

			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			expect(textArea.value).toBe('Hello world');
		});

		test('switches between voice types', async () => {
			render(<TextToSpeech />);

			// Wait for clones to load
			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Initially clone voice type is selected
			expect(screen.getByDisplayValue('clone')).toBeChecked();
			expect(screen.getByText('Select Voice Clone')).toBeInTheDocument();

			// Switch to system voices
			const systemRadio = screen.getByDisplayValue('system');
			fireEvent.click(systemRadio);

			expect(systemRadio).toBeChecked();
			expect(screen.getByText('Select System Voice')).toBeInTheDocument();
		});

		test('resets voice selection when switching voice types', async () => {
			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Select a voice clone
			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });
			expect(voiceSelect.value).toBe('clone1');

			// Switch to system voices
			const systemRadio = screen.getByDisplayValue('system');
			fireEvent.click(systemRadio);

			// Voice selection should be reset
			const systemVoiceSelect = screen.getByLabelText('Select System Voice');
			expect(systemVoiceSelect.value).toBe('');
		});

		test('shows selected voice clone information', async () => {
			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Select a voice clone
			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			// Should show voice clone information
			expect(screen.getByText('Selected Voice Clone')).toBeInTheDocument();
			expect(screen.getByText('Test Voice 1')).toBeInTheDocument();
			expect(screen.getByText('en-US')).toBeInTheDocument();
			expect(screen.getByText('ready')).toBeInTheDocument();
		});

		test('updates configuration settings', () => {
			render(<TextToSpeech />);

			// Update language
			const languageSelect = screen.getByLabelText('Language');
			fireEvent.change(languageSelect, { target: { value: 'fr-FR' } });
			expect(languageSelect.value).toBe('fr-FR');

			// Update speed
			const speedSelect = screen.getByLabelText('Speed');
			fireEvent.change(speedSelect, { target: { value: '1.25' } });
			expect(speedSelect.value).toBe('1.25');

			// Update pitch
			const pitchSelect = screen.getByLabelText('Pitch');
			fireEvent.change(pitchSelect, { target: { value: '0.75' } });
			expect(pitchSelect.value).toBe('0.75');

			// Update volume
			const volumeSelect = screen.getByLabelText('Volume');
			fireEvent.change(volumeSelect, { target: { value: '1.25' } });
			expect(volumeSelect.value).toBe('1.25');
		});
	});

	describe('Form Validation', () => {
		test('submit button is disabled when text is empty', async () => {
			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			const submitButton = screen.getByRole('button', { name: /generate/i });
			expect(submitButton).toBeDisabled();
		});

		test('submit button is disabled when voice is not selected', () => {
			render(<TextToSpeech />);

			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const submitButton = screen.getByRole('button', { name: /generate/i });
			expect(submitButton).toBeDisabled();
		});

		test('submit button is enabled when both text and voice are provided', async () => {
			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			const submitButton = screen.getByRole('button', { name: /generate/i });
			expect(submitButton).not.toBeDisabled();
		});
	});

	describe('Speech Generation', () => {
		test('generates speech with voice clone', async () => {
			voiceCloneService.synthesizeWithClone.mockResolvedValue({
				success: true,
				data: {
					job_id: 'job123',
					output_path: '/path/to/audio.wav',
				},
			});

			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Fill form
			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			// Submit form
			const submitButton = screen.getByRole('button', { name: /generate with voice clone/i });
			fireEvent.click(submitButton);

			// Should show generating state
			expect(screen.getByText('Generating...')).toBeInTheDocument();
			expect(screen.getByText('Generating')).toBeInTheDocument();

			await waitFor(() => {
				expect(voiceCloneService.synthesizeWithClone).toHaveBeenCalledWith(
					'clone1',
					'Hello world',
					{
						language: 'en-US',
						outputFormat: 'wav',
						sampleRate: 22050,
					}
				);
			});

			// Should show generated audio section
			await waitFor(() => {
				expect(screen.getByText('Generated Audio')).toBeInTheDocument();
			});
		});

		test('generates speech with system voice', async () => {
			jobService.createSynthesisJob.mockResolvedValue({
				success: true,
				data: {
					job_id: 'job456',
					output_path: '/path/to/audio.wav',
				},
			});

			render(<TextToSpeech />);

			// Switch to system voices
			const systemRadio = screen.getByDisplayValue('system');
			fireEvent.click(systemRadio);

			// Fill form
			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const voiceSelect = screen.getByLabelText('Select System Voice');
			fireEvent.change(voiceSelect, { target: { value: 'voice1' } });

			// Submit form
			const submitButton = screen.getByRole('button', { name: /generate speech/i });
			fireEvent.click(submitButton);

			await waitFor(() => {
				expect(jobService.createSynthesisJob).toHaveBeenCalledWith(
					'voice1',
					'Hello world',
					expect.objectContaining({
						speed: 1.0,
						pitch: 1.0,
						volume: 1.0,
						outputFormat: 'wav',
						sampleRate: 22050,
						language: 'en-US',
					})
				);
			});

			// Should show generated audio section
			await waitFor(() => {
				expect(screen.getByText('Generated Audio')).toBeInTheDocument();
			});
		});

		test('handles generation error', async () => {
			const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
			voiceCloneService.synthesizeWithClone.mockRejectedValue(new Error('Generation failed'));

			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Fill form
			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			// Submit form
			const submitButton = screen.getByRole('button', { name: /generate with voice clone/i });
			fireEvent.click(submitButton);

			await waitFor(() => {
				expect(alertSpy).toHaveBeenCalledWith('Failed to generate speech: Generation failed');
			});

			alertSpy.mockRestore();
		});

		test('shows progress during generation', async () => {
			// Mock slow generation
			voiceCloneService.synthesizeWithClone.mockImplementation(() => 
				new Promise(resolve => setTimeout(() => resolve({ success: true, data: { job_id: 'job123' } }), 1000))
			);

			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Fill form
			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			// Submit form
			const submitButton = screen.getByRole('button', { name: /generate with voice clone/i });
			fireEvent.click(submitButton);

			// Should show progress
			expect(screen.getByText('Generating')).toBeInTheDocument();
			expect(screen.getByText(/\d+% complete/)).toBeInTheDocument();

			// Wait for completion
			await waitFor(() => {
				expect(screen.getByText('Generated Audio')).toBeInTheDocument();
			}, { timeout: 1500 });
		});

		test('disables form inputs during generation', async () => {
			// Mock slow generation
			voiceCloneService.synthesizeWithClone.mockImplementation(() => 
				new Promise(resolve => setTimeout(() => resolve({ success: true, data: { job_id: 'job123' } }), 100))
			);

			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Fill form
			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			// Submit form
			const submitButton = screen.getByRole('button', { name: /generate with voice clone/i });
			fireEvent.click(submitButton);

			// Inputs should be disabled
			expect(textArea).toBeDisabled();
			expect(voiceSelect).toBeDisabled();
			expect(screen.getByLabelText('Language')).toBeDisabled();

			// Wait for completion
			await waitFor(() => {
				expect(textArea).not.toBeDisabled();
			});
		});
	});

	describe('Audio Player Controls', () => {
		const setupGeneratedAudio = async () => {
			voiceCloneService.synthesizeWithClone.mockResolvedValue({
				success: true,
				data: {
					job_id: 'job123',
					output_path: '/path/to/audio.wav',
				},
			});

			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Generate audio
			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			const submitButton = screen.getByRole('button', { name: /generate with voice clone/i });
			fireEvent.click(submitButton);

			await waitFor(() => {
				expect(screen.getByText('Generated Audio')).toBeInTheDocument();
			});
		};

		test('displays generated audio information', async () => {
			await setupGeneratedAudio();

			expect(screen.getByText('Hello world')).toBeInTheDocument();
			expect(screen.getByText('Voice Clone')).toBeInTheDocument();
			expect(screen.getByText('Test Voice 1')).toBeInTheDocument();
			expect(screen.getByText('en-US')).toBeInTheDocument();
		});

		test('plays audio when play button is clicked', async () => {
			global.fetch.mockResolvedValue({
				ok: true,
				blob: () => Promise.resolve(new Blob(['audio data'])),
			});

			await setupGeneratedAudio();

			const playButton = screen.getByText('Play').closest('button');
			fireEvent.click(playButton);

			await waitFor(() => {
				expect(global.fetch).toHaveBeenCalledWith(
					'https://api.example.com/file/voice-clone/job123',
					expect.objectContaining({
						method: 'GET',
						headers: {
							Authorization: 'Bearer mock_token',
						},
					})
				);
			});

			expect(URL.createObjectURL).toHaveBeenCalled();
			expect(mockAudio.play).toHaveBeenCalled();
		});

		test('pauses audio when pause button is clicked', async () => {
			await setupGeneratedAudio();

			// First click to play
			const playButton = screen.getByText('Play').closest('button');
			fireEvent.click(playButton);

			// Should show pause button
			await waitFor(() => {
				expect(screen.getByText('Pause')).toBeInTheDocument();
			});

			// Click to pause
			const pauseButton = screen.getByText('Pause').closest('button');
			fireEvent.click(pauseButton);

			expect(mockAudio.pause).toHaveBeenCalled();
		});

		test('downloads audio when download button is clicked', async () => {
			global.fetch.mockResolvedValue({
				ok: true,
				blob: () => Promise.resolve(new Blob(['audio data'])),
			});

			await setupGeneratedAudio();

			const downloadButton = screen.getByText('Download').closest('button');
			fireEvent.click(downloadButton);

			await waitFor(() => {
				expect(global.fetch).toHaveBeenCalledWith(
					'https://api.example.com/file/voice-clone/job123',
					expect.objectContaining({
						method: 'GET',
						headers: {
							Authorization: 'Bearer mock_token',
						},
					})
				);
			});

			expect(mockLink.download).toBe('speech_job123.wav');
			expect(mockLink.click).toHaveBeenCalled();
		});

		test('handles audio download error', async () => {
			const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
			global.fetch.mockRejectedValue(new Error('Download failed'));

			await setupGeneratedAudio();

			const downloadButton = screen.getByText('Download').closest('button');
			fireEvent.click(downloadButton);

			await waitFor(() => {
				expect(alertSpy).toHaveBeenCalledWith('Unable to download audio file');
			});

			alertSpy.mockRestore();
		});

		test('resets form when generate new button is clicked', async () => {
			await setupGeneratedAudio();

			const generateNewButton = screen.getByText('Generate New').closest('button');
			fireEvent.click(generateNewButton);

			// Generated audio section should be hidden
			expect(screen.queryByText('Generated Audio')).not.toBeInTheDocument();

			// Form should be reset
			expect(screen.getByLabelText('Text').value).toBe('');
			expect(screen.getByLabelText('Select Voice Clone').value).toBe('');
		});
	});

	describe('Voice Clones Empty State', () => {
		test('shows message when no voice clones available', async () => {
			voiceCloneService.listVoiceClones.mockResolvedValue({
				success: true,
				data: { clones: [] },
			});

			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('No voice clones available. Create one in Voice Clone page.')).toBeInTheDocument();
			});
		});
	});

	describe('Error Handling', () => {
		const setupGeneratedAudio = async () => {
			voiceCloneService.synthesizeWithClone.mockResolvedValue({
				success: true,
				data: {
					job_id: 'job123',
					output_path: '/path/to/audio.wav',
				},
			});

			render(<TextToSpeech />);

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			// Generate audio
			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			const submitButton = screen.getByRole('button', { name: /generate with voice clone/i });
			fireEvent.click(submitButton);

			await waitFor(() => {
				expect(screen.getByText('Generated Audio')).toBeInTheDocument();
			});
		};

		test('handles audio playback error', async () => {
			const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
			global.fetch.mockRejectedValue(new Error('Fetch failed'));

			await setupGeneratedAudio();

			const playButton = screen.getByText('Play').closest('button');
			fireEvent.click(playButton);

			await waitFor(() => {
				expect(alertSpy).toHaveBeenCalledWith('Unable to play audio file');
			});

			alertSpy.mockRestore();
		});

		test('handles fetch audio error', async () => {
			const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
			global.fetch.mockResolvedValue({
				ok: false,
				status: 404,
			});

			await setupGeneratedAudio();

			const playButton = screen.getByText('Play').closest('button');
			fireEvent.click(playButton);

			await waitFor(() => {
				expect(consoleSpy).toHaveBeenCalledWith('Failed to play audio:', expect.any(Error));
			});
			
			consoleSpy.mockRestore();
		});
	});

	describe('Accessibility', () => {
		test('form elements have proper labels', () => {
			render(<TextToSpeech />);

			expect(screen.getByLabelText('Text')).toBeInTheDocument();
			expect(screen.getByLabelText('Voice Type')).toBeInTheDocument();
			expect(screen.getByLabelText('Language')).toBeInTheDocument();
			expect(screen.getByLabelText('Speed')).toBeInTheDocument();
			expect(screen.getByLabelText('Pitch')).toBeInTheDocument();
			expect(screen.getByLabelText('Volume')).toBeInTheDocument();
		});

		test('submit button has proper disabled state', async () => {
			render(<TextToSpeech />);

			const submitButton = screen.getByRole('button', { name: /generate/i });
			expect(submitButton).toHaveAttribute('disabled');

			// Fill form
			const textArea = screen.getByLabelText('Text');
			fireEvent.change(textArea, { target: { value: 'Hello world' } });

			await waitFor(() => {
				expect(screen.getByText('Test Voice 1 (en-US) - ready')).toBeInTheDocument();
			});

			const voiceSelect = screen.getByLabelText('Select Voice Clone');
			fireEvent.change(voiceSelect, { target: { value: 'clone1' } });

			expect(submitButton).not.toHaveAttribute('disabled');
		});
	});
});