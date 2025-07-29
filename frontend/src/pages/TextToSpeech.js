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

const TextToSpeech = () => {
  const [text, setText] = useState('');
  const [voice, setVoice] = useState('');
  const [voiceType, setVoiceType] = useState('clone'); // 'clone' or 'system'
  const [voiceClones, setVoiceClones] = useState([]);
  const [loadingClones, setLoadingClones] = useState(true);
  const [config, setConfig] = useState({
    speed: 1.0,
    pitch: 1.0,
    volume: 1.0,
    outputFormat: 'wav',
    sampleRate: 22050,
    language: 'en-US',
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [generatedAudio, setGeneratedAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  // Load voice clones on component mount
  useEffect(() => {
    const loadVoiceClones = async () => {
      try {
        setLoadingClones(true);
        const response = await voiceCloneService.listVoiceClones();
        if (response.success) {
          setVoiceClones(response.data.clones || []);
        }
      } catch (error) {
        console.error('Failed to load voice clones:', error);
        setVoiceClones([]);
      } finally {
        setLoadingClones(false);
      }
    };

    loadVoiceClones();
  }, []);

  // Audio control functions
  const handlePlayPause = async () => {
    if (!generatedAudio?.jobId) return;

    if (isPlaying) {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      setIsPlaying(false);
    } else {
      try {
        // If audio source is not set, fetch it first
        if (!audioRef.current?.src || audioRef.current.src === '') {
          const audioBlob = await fetchAudioBlob(
            generatedAudio.jobId,
            generatedAudio.voiceType === 'clone'
          );
          if (audioBlob && audioRef.current) {
            const audioUrl = URL.createObjectURL(audioBlob);
            audioRef.current.src = audioUrl;
          }
        }

        if (audioRef.current) {
          await audioRef.current.play();
          setIsPlaying(true);
        }
      } catch (error) {
        console.error('Failed to play audio:', error);
        alert('Unable to play audio file');
      }
    }
  };

  const fetchAudioBlob = async (jobId, isVoiceClone) => {
    try {
      const endpoint = isVoiceClone
        ? `/file/voice-clone/${jobId}`
        : `/file/synthesis/${jobId}`;
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${apiConfig.apiBaseUrl}${endpoint}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch audio: ${response.status}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('Error fetching audio:', error);
      throw error;
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleAudioError = (e) => {
    console.error('Audio playback error:', e);
    setIsPlaying(false);
    alert('Unable to play audio file');
  };

  const handleDownload = async () => {
    if (!generatedAudio?.jobId) return;

    try {
      const audioBlob = await fetchAudioBlob(
        generatedAudio.jobId,
        generatedAudio.voiceType === 'clone'
      );
      const audioUrl = URL.createObjectURL(audioBlob);

      const link = document.createElement('a');
      link.href = audioUrl;
      link.download = `speech_${generatedAudio.jobId}.wav`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up the URL after download
      setTimeout(() => URL.revokeObjectURL(audioUrl), 1000);
    } catch (error) {
      console.error('Failed to download audio:', error);
      alert('Unable to download audio file');
    }
  };

  const handleNewGeneration = () => {
    setGeneratedAudio(null);
    setIsPlaying(false);
    setText('');
    setVoice('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim() || !voice) return;

    setIsGenerating(true);

    try {
      // Simulate progress while actually generating
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      let result;
      if (voiceType === 'clone') {
        // Use voice clone synthesis
        result = await voiceCloneService.synthesizeWithClone(voice, text, {
          language: config.language,
          outputFormat: config.outputFormat,
          sampleRate: config.sampleRate,
        });
      } else {
        // Use traditional synthesis job
        result = await jobService.createSynthesisJob(voice, text, config);
      }

      setProgress(100);

      if (result.success) {
        // Store generated audio information
        setGeneratedAudio({
          text: text,
          audioPath: result.data?.output_path,
          jobId: result.data?.job_id,
          language: config.language,
          voiceType: voiceType,
          voiceName:
            voiceType === 'clone'
              ? voiceClones.find((clone) => clone.clone_id === voice)?.name
              : voice,
          createdAt: new Date().toISOString(),
        });

        // Don't reset form immediately, let user play the audio first
        // setText('');
        // setVoice('');
      }
    } catch (error) {
      console.error('Failed to generate speech:', error);
      alert(`Failed to generate speech: ${error.message || error}`);
    } finally {
      setIsGenerating(false);
      setProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-12">Text to Speech</h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Text Input */}
          <div>
            <label
              htmlFor="text"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              Text
            </label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors h-48 resize-none"
              placeholder="Enter the text you want to convert to speech"
              disabled={isGenerating}
            />
          </div>

          {/* Voice Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Voice Type
            </label>
            <div className="flex space-x-4 mb-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="clone"
                  checked={voiceType === 'clone'}
                  onChange={(e) => {
                    setVoiceType(e.target.value);
                    setVoice(''); // Reset voice selection when type changes
                  }}
                  className="mr-2"
                  disabled={isGenerating}
                />
                <span className="text-white">Voice Clones</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="system"
                  checked={voiceType === 'system'}
                  onChange={(e) => {
                    setVoiceType(e.target.value);
                    setVoice(''); // Reset voice selection when type changes
                  }}
                  className="mr-2"
                  disabled={isGenerating}
                />
                <span className="text-white">System Voices</span>
              </label>
            </div>
          </div>

          {/* Voice Selection */}
          <div>
            <label
              htmlFor="voice"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              {voiceType === 'clone'
                ? 'Select Voice Clone'
                : 'Select System Voice'}
            </label>
            {voiceType === 'clone' ? (
              <select
                id="voice"
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                disabled={isGenerating || loadingClones}
              >
                <option value="">
                  {loadingClones
                    ? 'Loading voice clones...'
                    : 'Select a voice clone'}
                </option>
                {voiceClones.map((clone) => (
                  <option key={clone.clone_id} value={clone.clone_id}>
                    {clone.name} ({clone.language}) - {clone.status}
                  </option>
                ))}
                {!loadingClones && voiceClones.length === 0 && (
                  <option value="" disabled>
                    No voice clones available. Create one in Voice Clone page.
                  </option>
                )}
              </select>
            ) : (
              <select
                id="voice"
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                disabled={isGenerating}
              >
                <option value="">Select a system voice</option>
                <option value="voice1">Voice 1</option>
                <option value="voice2">Voice 2</option>
              </select>
            )}
          </div>

          {/* Selected Voice Clone Info */}
          {voiceType === 'clone' && voice && (
            <div className="bg-zinc-900 border border-zinc-800 rounded p-4">
              <h3 className="text-lg font-semibold mb-2">
                Selected Voice Clone
              </h3>
              {(() => {
                const selectedClone = voiceClones.find(
                  (clone) => clone.clone_id === voice
                );
                if (selectedClone) {
                  return (
                    <div className="space-y-2 text-sm text-gray-300">
                      <div>
                        <strong>Name:</strong> {selectedClone.name}
                      </div>
                      <div>
                        <strong>Language:</strong> {selectedClone.language}
                      </div>
                      <div>
                        <strong>Status:</strong>{' '}
                        <span
                          className={`${selectedClone.status === 'ready' ? 'text-green-400' : 'text-yellow-400'}`}
                        >
                          {selectedClone.status}
                        </span>
                      </div>
                      <div>
                        <strong>Created:</strong>{' '}
                        {new Date(
                          selectedClone.created_at
                        ).toLocaleDateString()}
                      </div>
                    </div>
                  );
                }
                return null;
              })()}
            </div>
          )}

          {/* Settings Section */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Settings</h2>
            <div className="space-y-4">
              {/* Language Selection */}
              <div>
                <label
                  htmlFor="language"
                  className="block text-sm font-medium text-gray-300 mb-2"
                >
                  Language
                </label>
                <select
                  id="language"
                  value={config.language}
                  onChange={(e) =>
                    setConfig((prev) => ({ ...prev, language: e.target.value }))
                  }
                  className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  disabled={isGenerating}
                >
                  {/* Native multilingual support */}
                  <optgroup label="Native Support (Best Quality)">
                    <option value="zh-CN">Chinese (Simplified)</option>
                    <option value="zh-TW">Chinese (Traditional)</option>
                    <option value="en-US">English (US)</option>
                    <option value="en-GB">English (UK)</option>
                  </optgroup>

                  {/* Specialized model support */}
                  <optgroup label="Specialized Models (High Quality)">
                    <option value="ja-JP">Japanese</option>
                    <option value="fr-FR">French</option>
                    <option value="de-DE">German</option>
                    <option value="es-ES">Spanish</option>
                    <option value="it-IT">Italian</option>
                    <option value="ru-RU">Russian</option>
                    <option value="hi-IN">Hindi</option>
                    <option value="fi-FI">Finnish</option>
                  </optgroup>

                  {/* Fallback support */}
                  <optgroup label="Basic Support (Limited Quality)">
                    <option value="ko-KR">Korean</option>
                    <option value="pt-BR">Portuguese</option>
                    <option value="ar-SA">Arabic</option>
                    <option value="th-TH">Thai</option>
                    <option value="vi-VN">Vietnamese</option>
                  </optgroup>
                </select>
              </div>

              {/* Speed Control */}
              <div>
                <label
                  htmlFor="speed"
                  className="block text-sm font-medium text-gray-300 mb-2"
                >
                  Speed
                </label>
                <select
                  id="speed"
                  value={config.speed}
                  onChange={(e) =>
                    setConfig((prev) => ({
                      ...prev,
                      speed: parseFloat(e.target.value),
                    }))
                  }
                  className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  disabled={isGenerating}
                >
                  <option value="0.75">Slow</option>
                  <option value="1.0">Normal</option>
                  <option value="1.25">Fast</option>
                </select>
              </div>

              {/* Pitch Control */}
              <div>
                <label
                  htmlFor="pitch"
                  className="block text-sm font-medium text-gray-300 mb-2"
                >
                  Pitch
                </label>
                <select
                  id="pitch"
                  value={config.pitch}
                  onChange={(e) =>
                    setConfig((prev) => ({
                      ...prev,
                      pitch: parseFloat(e.target.value),
                    }))
                  }
                  className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  disabled={isGenerating}
                >
                  <option value="0.75">Low</option>
                  <option value="1.0">Normal</option>
                  <option value="1.25">High</option>
                </select>
              </div>

              {/* Volume Control */}
              <div>
                <label
                  htmlFor="volume"
                  className="block text-sm font-medium text-gray-300 mb-2"
                >
                  Volume
                </label>
                <select
                  id="volume"
                  value={config.volume}
                  onChange={(e) =>
                    setConfig((prev) => ({
                      ...prev,
                      volume: parseFloat(e.target.value),
                    }))
                  }
                  className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  disabled={isGenerating}
                >
                  <option value="0.75">Quiet</option>
                  <option value="1.0">Normal</option>
                  <option value="1.25">Loud</option>
                </select>
              </div>
            </div>
          </div>

          {/* Generation Progress */}
          {isGenerating && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Generating</span>
                <span>{progress}% complete</span>
              </div>
              <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                <div
                  className="h-full bg-white transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              disabled={!text.trim() || !voice || isGenerating}
              className={`w-full px-6 py-3 rounded text-center font-semibold border-2 border-white hover:bg-white hover:text-black transition-colors ${
                !text.trim() || !voice || isGenerating
                  ? 'opacity-50 cursor-not-allowed'
                  : ''
              }`}
            >
              {isGenerating
                ? 'Generating...'
                : voiceType === 'clone'
                  ? 'Generate with Voice Clone'
                  : 'Generate speech'}
            </button>
          </div>
        </form>

        {/* Generated Audio Player */}
        {generatedAudio && (
          <div className="mt-8 bg-zinc-900 border border-zinc-800 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Generated Audio</h2>

            {/* Audio Information */}
            <div className="mb-4 space-y-2 text-sm text-gray-300">
              <div>
                <strong>Text:</strong>{' '}
                {generatedAudio.text.length > 100
                  ? `${generatedAudio.text.substring(0, 100)}...`
                  : generatedAudio.text}
              </div>
              <div>
                <strong>Voice Type:</strong>{' '}
                {generatedAudio.voiceType === 'clone'
                  ? 'Voice Clone'
                  : 'System Voice'}
              </div>
              <div>
                <strong>Voice Name:</strong> {generatedAudio.voiceName}
              </div>
              <div>
                <strong>Language:</strong> {generatedAudio.language}
              </div>
              <div>
                <strong>Generated At:</strong>{' '}
                {new Date(generatedAudio.createdAt).toLocaleString('en-US')}
              </div>
            </div>

            {/* Audio Player Controls */}
            <div className="flex items-center space-x-4 mb-4">
              <button
                onClick={handlePlayPause}
                className="flex items-center space-x-2 px-4 py-2 bg-white text-black rounded hover:bg-gray-200 transition-colors"
              >
                <span>{isPlaying ? '⏸️' : '▶️'}</span>
                <span>{isPlaying ? 'Pause' : 'Play'}</span>
              </button>

              <button
                onClick={handleDownload}
                className="flex items-center space-x-2 px-4 py-2 border border-white text-white rounded hover:bg-white hover:text-black transition-colors"
              >
                <span>⬇️</span>
                <span>Download</span>
              </button>

              <button
                onClick={handleNewGeneration}
                className="flex items-center space-x-2 px-4 py-2 border border-zinc-600 text-gray-300 rounded hover:bg-zinc-800 transition-colors"
              >
                <span>🔄</span>
                <span>Generate New</span>
              </button>
            </div>

            {/* Hidden Audio Element */}
            <audio
              ref={audioRef}
              onEnded={handleAudioEnded}
              onError={handleAudioError}
              preload="none"
              className="hidden"
            />

            {/* Audio Waveform Visualization (placeholder) */}
            <div className="h-16 bg-zinc-800 rounded flex items-center justify-center text-gray-400">
              <span>
                🎵 Audio Waveform (Playing: {isPlaying ? 'Yes' : 'No'})
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
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