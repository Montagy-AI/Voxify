import jobService from '../job.service';

// Import the mocked api
import api from '../api';

// Mock the api module
jest.mock('../api', () => ({
  post: jest.fn(),
  get: jest.fn(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Setup mocks
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('JobService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue('mock_access_token');
  });

  /*
   * Test cases for getSynthesisJobs.
   */
  describe('getSynthesisJobs', () => {
    const mockSuccessResponse = {
      data: {
        success: true,
        data: [
          {
            id: 1,
            voice_model_id: 123,
            text_content: 'Hello world',
            status: 'completed',
            created_at: '2025-01-01T00:00:00Z',
          },
          {
            id: 2,
            voice_model_id: 456,
            text_content: 'Another test',
            status: 'processing',
            created_at: '2025-01-01T01:00:00Z',
          },
        ],
      },
    };

    test('Successfully gets synthesis jobs', async () => {
      api.get.mockResolvedValue(mockSuccessResponse);
      const result = await jobService.getSynthesisJobs();
      expect(api.get).toHaveBeenCalledWith('/job', {
        params: {
          sort_by: 'created_at',
          sort_order: 'desc',
          limit: 100,
        },
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data.data);
    });

    test('Returns empty array when no jobs found (404)', async () => {
      const mock404Error = {
        response: {
          status: 404,
        },
      };
      api.get.mockRejectedValue(mock404Error);
      const result = await jobService.getSynthesisJobs();
      expect(result).toEqual([]);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(jobService.getSynthesisJobs()).rejects.toThrow(
        'No authentication token found'
      );
      expect(api.get).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails (non-404)', async () => {
      const mockError = {
        response: {
          status: 500,
          data: {
            error: 'Internal server error',
          },
        },
      };
      api.get.mockRejectedValue(mockError);
      await expect(jobService.getSynthesisJobs()).rejects.toBe(
        'Internal server error'
      );
    });

    test('Throws generic error when API request fails without response data', async () => {
      const mockError = new Error('Network error');
      api.get.mockRejectedValue(mockError);
      await expect(jobService.getSynthesisJobs()).rejects.toBe(mockError);
    });
  });

  /*
   * Test cases for getSynthesisJob.
   */
  describe('getSynthesisJob', () => {
    const mockJobId = 123;
    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          id: 123,
          voice_model_id: 456,
          text_content: 'Test synthesis job',
          status: 'completed',
          output_url: '/path/to/output.wav',
          created_at: '2025-01-01T00:00:00Z',
          completed_at: '2025-01-01T00:05:00Z',
        },
      },
    };

    test('Successfully gets synthesis job by ID', async () => {
      api.get.mockResolvedValue(mockSuccessResponse);
      const result = await jobService.getSynthesisJob(mockJobId);
      expect(api.get).toHaveBeenCalledWith(`/job/${mockJobId}`, {
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(jobService.getSynthesisJob(mockJobId)).rejects.toThrow(
        'No authentication token found'
      );
      expect(api.get).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Job not found',
          },
        },
      };
      api.get.mockRejectedValue(mockError);
      await expect(jobService.getSynthesisJob(mockJobId)).rejects.toBe(
        'Job not found'
      );
    });

    test('Throws generic error when API request fails without response data', async () => {
      const mockError = new Error('Network error');
      api.get.mockRejectedValue(mockError);
      await expect(jobService.getSynthesisJob(mockJobId)).rejects.toBe(
        mockError
      );
    });
  });

  /*
   * Test cases for createSynthesisJob.
   */
  describe('createSynthesisJob', () => {
    const mockVoiceModelId = 456;
    const mockText = 'Hello, this is a test synthesis job.';
    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          id: 789,
          voice_model_id: 456,
          text_content: mockText,
          status: 'queued',
          created_at: '2025-01-01T00:00:00Z',
        },
      },
    };

    test('Successfully creates synthesis job with default config', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await jobService.createSynthesisJob(
        mockVoiceModelId,
        mockText
      );
      expect(api.post).toHaveBeenCalledWith(
        '/job',
        {
          voice_model_id: mockVoiceModelId,
          text_content: mockText,
          output_format: 'wav',
          sample_rate: 22050,
          speed: 1.0,
          pitch: 1.0,
          volume: 1.0,
        },
        {
          headers: {
            Authorization: 'Bearer mock_access_token',
          },
        }
      );

      expect(result).toEqual(mockSuccessResponse.data.data);
    });

    test('Successfully creates synthesis job with custom config', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const customConfig = {
        outputFormat: 'mp3',
        sampleRate: 44100,
        speed: 1.2,
        pitch: 0.9,
        volume: 0.8,
      };
      const result = await jobService.createSynthesisJob(
        mockVoiceModelId,
        mockText,
        customConfig
      );
      expect(api.post).toHaveBeenCalledWith(
        '/job',
        {
          voice_model_id: mockVoiceModelId,
          text_content: mockText,
          output_format: 'mp3',
          sample_rate: 44100,
          speed: 1.2,
          pitch: 0.9,
          volume: 0.8,
        },
        {
          headers: {
            Authorization: 'Bearer mock_access_token',
          },
        }
      );
      expect(result).toEqual(mockSuccessResponse.data.data);
    });

    test('Successfully creates synthesis job with partial custom config', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const partialConfig = {
        outputFormat: 'mp3',
        speed: 1.5,
      };
      const result = await jobService.createSynthesisJob(
        mockVoiceModelId,
        mockText,
        partialConfig
      );
      expect(api.post).toHaveBeenCalledWith(
        '/job',
        {
          voice_model_id: mockVoiceModelId,
          text_content: mockText,
          output_format: 'mp3',
          sample_rate: 22050, // default
          speed: 1.5,
          pitch: 1.0, // default
          volume: 1.0, // default
        },
        {
          headers: {
            Authorization: 'Bearer mock_access_token',
          },
        }
      );
      expect(result).toEqual(mockSuccessResponse.data.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(
        jobService.createSynthesisJob(mockVoiceModelId, mockText)
      ).rejects.toThrow('No authentication token found');
      expect(api.post).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Failed to create synthesis job',
          },
        },
      };
      api.post.mockRejectedValue(mockError);
      await expect(
        jobService.createSynthesisJob(mockVoiceModelId, mockText)
      ).rejects.toBe('Failed to create synthesis job');
    });

    test('Throws generic error when API request fails without response data', async () => {
      const mockError = new Error('Network error');
      api.post.mockRejectedValue(mockError);
      await expect(
        jobService.createSynthesisJob(mockVoiceModelId, mockText)
      ).rejects.toBe(mockError);
    });
  });

  /*
   * Test cases for cancelSynthesisJob.
   */
  describe('cancelSynthesisJob', () => {
    const mockJobId = 789;
    const mockSuccessResponse = {
      data: {
        success: true,
        message: 'Job cancelled successfully',
      },
    };

    test('Successfully cancels synthesis job', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await jobService.cancelSynthesisJob(mockJobId);
      expect(api.post).toHaveBeenCalledWith(
        `/job/${mockJobId}/cancel`,
        {},
        {
          headers: {
            Authorization: 'Bearer mock_access_token',
          },
        }
      );

      expect(result).toBe(true);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(jobService.cancelSynthesisJob(mockJobId)).rejects.toThrow(
        'No authentication token found'
      );
      expect(api.post).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Failed to cancel job',
          },
        },
      };
      api.post.mockRejectedValue(mockError);
      await expect(jobService.cancelSynthesisJob(mockJobId)).rejects.toBe(
        'Failed to cancel job'
      );
    });

    test('Throws generic error when API request fails without response data', async () => {
      const mockError = new Error('Network error');
      api.post.mockRejectedValue(mockError);
      await expect(jobService.cancelSynthesisJob(mockJobId)).rejects.toBe(
        mockError
      );
    });
  });

  /*
   * Test cases for downloadSynthesisOutput.
   */
  describe('downloadSynthesisOutput', () => {
    const mockJobId = 789;
    const mockBlobData = new Blob(['mock audio data'], { type: 'audio/wav' });

    test('Successfully downloads synthesis output', async () => {
      api.get.mockResolvedValue({ data: mockBlobData });
      const result = await jobService.downloadSynthesisOutput(mockJobId);
      expect(api.get).toHaveBeenCalledWith(`/job/${mockJobId}/download`, {
        responseType: 'blob',
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toBe(mockBlobData);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(
        jobService.downloadSynthesisOutput(mockJobId)
      ).rejects.toThrow('No authentication token found');
      expect(api.get).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'File not found',
          },
        },
      };
      api.get.mockRejectedValue(mockError);
      await expect(jobService.downloadSynthesisOutput(mockJobId)).rejects.toBe(
        'File not found'
      );
    });

    test('Throws generic error when API request fails without response data', async () => {
      const mockError = new Error('Network error');
      api.get.mockRejectedValue(mockError);
      await expect(jobService.downloadSynthesisOutput(mockJobId)).rejects.toBe(
        mockError
      );
    });
  });
});
