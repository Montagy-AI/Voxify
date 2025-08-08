import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import VoiceClone from '../VoiceClone';

// Import mocked services
import voiceCloneService from '../../services/voiceClone.service';

// Mock the voiceClone service
jest.mock('../../services/voiceClone.service', () => ({
  uploadVoiceSample: jest.fn(),
  createVoiceClone: jest.fn(),
  listVoiceClones: jest.fn(),
  deleteVoiceClone: jest.fn(),
  synthesizeVoice: jest.fn(),
  getVoiceClone: jest.fn(),
  deleteVoiceSample: jest.fn(),
  getVoiceSamples: jest.fn(),
}));

// Mock react-router-dom hooks
const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Helper component to wrap VoiceClone with Router
const VoiceCloneWithRouter = () => (
  <BrowserRouter>
    <VoiceClone />
  </BrowserRouter>
);

// Helper function to create mock files
const createMockFile = (name = 'test-audio.wav', size = 1024000) => {
  const file = new File(['mock audio content'], name, {
    type: 'audio/wav',
    lastModified: Date.now(),
  });
  // Ensure the size property is properly set for testing
  Object.defineProperty(file, 'size', {
    value: size,
    writable: false,
  });
  return file;
};

describe('VoiceClone Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.alert.mockClear();
    mockNavigate.mockClear();
  });

  describe('Initial Render', () => {
    test('renders main heading and form elements', () => {
      render(<VoiceCloneWithRouter />);

      expect(screen.getByText('Clone your voice')).toBeInTheDocument();
      expect(screen.getByLabelText('Clone Name *')).toBeInTheDocument();
      expect(screen.getByLabelText('Description')).toBeInTheDocument();
      expect(screen.getByLabelText('Reference Text *')).toBeInTheDocument();
      expect(screen.getByLabelText('Language')).toBeInTheDocument();
      expect(screen.getByText('Upload voice samples')).toBeInTheDocument();
    });

    test('renders all language options correctly', () => {
      render(<VoiceCloneWithRouter />);

      const languageSelect = screen.getByLabelText('Language');
      expect(languageSelect).toHaveValue('zh-CN'); // Default value

      // Check for some key language options
      expect(screen.getByText('Chinese (Simplified)')).toBeInTheDocument();
      expect(screen.getByText('English (US)')).toBeInTheDocument();
      expect(screen.getByText('Japanese')).toBeInTheDocument();
      expect(screen.getByText('Korean')).toBeInTheDocument();
    });

    test('renders file upload section with drag and drop zone', () => {
      render(<VoiceCloneWithRouter />);

      expect(screen.getByText('Drag and drop files here')).toBeInTheDocument();
      expect(screen.getByText('Or click to browse')).toBeInTheDocument();
      expect(screen.getByText('Browse Files')).toBeInTheDocument();
    });

    test('submit button is initially disabled', () => {
      render(<VoiceCloneWithRouter />);

      const submitButton = screen.getByText('Create Voice Clone');
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveClass('opacity-50', 'cursor-not-allowed');
    });
  });

  describe('Form Input Handling', () => {
    test('updates name input correctly', () => {
      render(<VoiceCloneWithRouter />);

      const nameInput = screen.getByLabelText('Clone Name *');
      fireEvent.change(nameInput, { target: { value: 'My Voice Clone' } });

      expect(nameInput).toHaveValue('My Voice Clone');
    });

    test('updates description input correctly', () => {
      render(<VoiceCloneWithRouter />);

      const descriptionInput = screen.getByLabelText('Description');
      fireEvent.change(descriptionInput, {
        target: { value: 'Test description' },
      });

      expect(descriptionInput).toHaveValue('Test description');
    });

    test('updates reference text input correctly', () => {
      render(<VoiceCloneWithRouter />);

      const refTextInput = screen.getByLabelText('Reference Text *');
      fireEvent.change(refTextInput, { target: { value: 'Hello world' } });

      expect(refTextInput).toHaveValue('Hello world');
    });

    test('updates language selection correctly', () => {
      render(<VoiceCloneWithRouter />);

      const languageSelect = screen.getByLabelText('Language');
      fireEvent.change(languageSelect, { target: { value: 'en-US' } });

      expect(languageSelect).toHaveValue('en-US');
    });
  });

  describe('File Selection', () => {
    test('handles file selection through input change', () => {
      render(<VoiceCloneWithRouter />);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFile = createMockFile();

      fireEvent.change(fileInput, {
        target: { files: [mockFile] },
      });

      expect(screen.getByText('test-audio.wav')).toBeInTheDocument();
      // Use a more flexible matcher for file size since it might be formatted differently
      expect(screen.getByText(/MB/)).toBeInTheDocument();
      expect(screen.getByText('Upload Samples')).toBeInTheDocument();
    });

    test('handles multiple file selection', () => {
      render(<VoiceCloneWithRouter />);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFiles = [
        createMockFile('audio1.wav', 500000),
        createMockFile('audio2.wav', 750000),
      ];

      fireEvent.change(fileInput, {
        target: { files: mockFiles },
      });

      expect(screen.getByText('audio1.wav')).toBeInTheDocument();
      expect(screen.getByText('audio2.wav')).toBeInTheDocument();
      // Use more flexible matchers for file sizes
      const mbElements = screen.getAllByText(/MB/);
      expect(mbElements.length).toBeGreaterThanOrEqual(2);
    });

    test('renders drag and drop zone', () => {
      render(<VoiceCloneWithRouter />);

      expect(screen.getByText('Drag and drop files here')).toBeInTheDocument();
      expect(screen.getByText('Or click to browse')).toBeInTheDocument();
      expect(screen.getByText('Browse Files')).toBeInTheDocument();
    });

    test('browse files button triggers file input click', () => {
      render(<VoiceCloneWithRouter />);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const clickSpy = jest
        .spyOn(fileInput, 'click')
        .mockImplementation(() => {});

      const browseButton = screen.getByText('Browse Files');
      fireEvent.click(browseButton);

      expect(clickSpy).toHaveBeenCalled();
      clickSpy.mockRestore();
    });
  });

  describe('File Upload', () => {
    test('successful file upload updates uploaded samples list', async () => {
      const mockUploadResponse = {
        success: true,
        data: {
          sample_id: 'sample-123',
          name: 'test-audio.wav',
        },
      };
      voiceCloneService.uploadVoiceSample.mockResolvedValue(mockUploadResponse);

      render(<VoiceCloneWithRouter />);

      // Add a file
      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFile = createMockFile();
      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      // Click upload
      const uploadButton = screen.getByText('Upload Samples');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(voiceCloneService.uploadVoiceSample).toHaveBeenCalledWith(
          mockFile,
          'test-audio.wav'
        );
      });

      await waitFor(() => {
        expect(screen.getByText('Uploaded Samples')).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText('Ready')).toBeInTheDocument();
      });

      expect(global.alert).toHaveBeenCalledWith(
        'Successfully uploaded 1 file(s)'
      );
    });

    test('handles upload failure with error alert', async () => {
      const mockUploadResponse = {
        success: false,
        error: 'Upload failed',
      };
      voiceCloneService.uploadVoiceSample.mockResolvedValue(mockUploadResponse);

      render(<VoiceCloneWithRouter />);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFile = createMockFile();
      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      const uploadButton = screen.getByText('Upload Samples');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(global.alert).toHaveBeenCalledWith(
          'Failed to upload test-audio.wav: Upload failed'
        );
      });
    });

    test('handles upload exception with error alert', async () => {
      voiceCloneService.uploadVoiceSample.mockRejectedValue(
        new Error('Network error')
      );

      render(<VoiceCloneWithRouter />);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFile = createMockFile();
      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      const uploadButton = screen.getByText('Upload Samples');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(global.alert).toHaveBeenCalledWith(
          'Failed to upload test-audio.wav: Network error'
        );
      });
    });

    test('shows upload progress during file upload', async () => {
      let resolveUpload;
      const uploadPromise = new Promise((resolve) => {
        resolveUpload = resolve;
      });
      voiceCloneService.uploadVoiceSample.mockReturnValue(uploadPromise);

      render(<VoiceCloneWithRouter />);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFile = createMockFile();
      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      const uploadButton = screen.getByText('Upload Samples');
      fireEvent.click(uploadButton);

      // Check for uploading state
      expect(screen.getByText('Uploading...')).toBeInTheDocument();
      expect(screen.getByText('Uploading')).toBeInTheDocument();
      expect(screen.getByText('0% complete')).toBeInTheDocument();

      // Complete the upload
      resolveUpload({
        success: true,
        data: { sample_id: 'sample-123', name: 'test-audio.wav' },
      });

      await waitFor(() => {
        expect(screen.queryByText('Uploading...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Voice Clone Creation', () => {
    const setupFormData = () => {
      const nameInput = screen.getByLabelText('Clone Name *');
      const refTextInput = screen.getByLabelText('Reference Text *');
      const descriptionInput = screen.getByLabelText('Description');
      const languageSelect = screen.getByLabelText('Language');

      fireEvent.change(nameInput, { target: { value: 'Test Clone' } });
      fireEvent.change(refTextInput, { target: { value: 'Hello world' } });
      fireEvent.change(descriptionInput, {
        target: { value: 'Test description' },
      });
      fireEvent.change(languageSelect, { target: { value: 'en-US' } });
    };

    test('successful voice clone creation navigates to dashboard', async () => {
      const mockCreateResponse = { success: true };
      voiceCloneService.createVoiceClone.mockResolvedValue(mockCreateResponse);

      // First, upload a sample to get uploaded samples
      const mockUploadResponse = {
        success: true,
        data: { sample_id: 'sample-123', name: 'test-audio.wav' },
      };
      voiceCloneService.uploadVoiceSample.mockResolvedValue(mockUploadResponse);

      render(<VoiceCloneWithRouter />);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFile = createMockFile();
      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      const uploadButton = screen.getByText('Upload Samples');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText('Uploaded Samples')).toBeInTheDocument();
      });

      // Clear the upload alert before proceeding
      global.alert.mockClear();

      // Fill form
      setupFormData();

      // Submit form by clicking the button
      const submitButton = screen.getByText('Create Voice Clone');

      // Wait for the button to be enabled
      await waitFor(() => {
        expect(submitButton).not.toBeDisabled();
      });

      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(voiceCloneService.createVoiceClone).toHaveBeenCalledWith({
          sample_ids: ['sample-123'],
          name: 'Test Clone',
          description: 'Test description',
          ref_text: 'Hello world',
          language: 'en-US',
        });
      });

      await waitFor(() => {
        expect(global.alert).toHaveBeenCalledWith(
          'Voice clone created successfully! 🎉'
        );
      });
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });

    test('handles voice clone creation failure', async () => {
      const mockCreateResponse = {
        success: false,
        error: 'Creation failed',
      };
      voiceCloneService.createVoiceClone.mockResolvedValue(mockCreateResponse);

      render(<VoiceCloneWithRouter />);

      // Setup uploaded samples
      const mockUploadResponse = {
        success: true,
        data: { sample_id: 'sample-123', name: 'test-audio.wav' },
      };
      voiceCloneService.uploadVoiceSample.mockResolvedValue(mockUploadResponse);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFile = createMockFile();
      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      const uploadButton = screen.getByText('Upload Samples');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText('Uploaded Samples')).toBeInTheDocument();
      });

      // Clear upload alert
      global.alert.mockClear();

      setupFormData();

      const submitButton = screen.getByText('Create Voice Clone');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(global.alert).toHaveBeenCalledWith(
          'Creation failed: Creation failed'
        );
      });

      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Form Validation', () => {
    test('prevents submission without uploaded samples', async () => {
      render(<VoiceCloneWithRouter />);

      const nameInput = screen.getByLabelText('Clone Name *');
      const refTextInput = screen.getByLabelText('Reference Text *');

      fireEvent.change(nameInput, { target: { value: 'Test Clone' } });
      fireEvent.change(refTextInput, { target: { value: 'Hello world' } });

      // The button should be disabled due to no uploaded samples
      const submitButton = screen.getByText('Create Voice Clone');
      expect(submitButton).toBeDisabled();
    });

    test('enables submission when all requirements are met', async () => {
      render(<VoiceCloneWithRouter />);

      const submitButton = screen.getByText('Create Voice Clone');
      expect(submitButton).toBeDisabled();

      // Upload a sample
      const mockUploadResponse = {
        success: true,
        data: { sample_id: 'sample-123', name: 'test-audio.wav' },
      };
      voiceCloneService.uploadVoiceSample.mockResolvedValue(mockUploadResponse);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      const mockFile = createMockFile();
      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      const uploadButton = screen.getByText('Upload Samples');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText('Uploaded Samples')).toBeInTheDocument();
      });

      // Fill required fields
      const nameInput = screen.getByLabelText('Clone Name *');
      const refTextInput = screen.getByLabelText('Reference Text *');

      fireEvent.change(nameInput, { target: { value: 'Test Clone' } });
      fireEvent.change(refTextInput, { target: { value: 'Hello world' } });

      expect(submitButton).not.toBeDisabled();
      expect(submitButton).not.toHaveClass('opacity-50', 'cursor-not-allowed');
    });
  });

  describe('Component Styling', () => {
    test('renders with main heading and form elements', () => {
      render(<VoiceCloneWithRouter />);

      expect(screen.getByText('Clone your voice')).toBeInTheDocument();
      expect(screen.getByLabelText('Clone Name *')).toBeInTheDocument();
      expect(screen.getByLabelText('Upload voice samples')).toBeInTheDocument();
    });

    test('file input has correct attributes', () => {
      render(<VoiceCloneWithRouter />);

      const fileInput = screen.getByLabelText('Upload voice samples', {
        selector: 'input[type="file"]',
      });
      expect(fileInput).toHaveAttribute('multiple');
      expect(fileInput).toHaveAttribute('accept', 'audio/*');
    });
  });
});
