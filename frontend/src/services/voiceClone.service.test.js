import voiceCloneService from './voiceClone.service';

// Mock the api module
jest.mock('./api', () => ({
  post: jest.fn(),
  get: jest.fn(),
  delete: jest.fn(),
}));

// Import the mocked api
import api from './api';

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

describe('VoiceCloneService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue('mock_access_token');
  });

  /*
   * Test cases for uploadVoiceSample.
   */
  describe('uploadVoiceSample', () => {
    const mockFile = new File(['test audio content'], 'test.wav', {
      type: 'audio/wav',
    });
    const mockOnProgress = jest.fn();

    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          id: 1,
          name: 'Test Sample',
          file_path: '/path/to/sample.wav',
          created_at: '2025-01-01T00:00:00Z',
        },
      },
    };

    test('Successfully uploads voice sample with provided name', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.uploadVoiceSample(
        mockFile,
        'Test Sample',
        mockOnProgress
      );
      expect(api.post).toHaveBeenCalledWith(
        '/voice/samples',
        expect.any(FormData),
        {
          headers: {
            Authorization: 'Bearer mock_access_token',
          },
          timeout: 300000,
          onUploadProgress: mockOnProgress,
        }
      );
      // Verify FormData contains correct data
      const callArgs = api.post.mock.calls[0];
      const formData = callArgs[1];
      expect(formData.get('file')).toBe(mockFile);
      expect(formData.get('name')).toBe('Test Sample');
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Successfully uploads voice sample with auto-generated name when name is empty', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.uploadVoiceSample(
        mockFile,
        '',
        mockOnProgress
      );
      const callArgs = api.post.mock.calls[0];
      const formData = callArgs[1];
      expect(formData.get('name')).toMatch(/^Sample_\d+$/);
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Successfully uploads voice sample with auto-generated name when name is undefined', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.uploadVoiceSample(
        mockFile,
        undefined,
        mockOnProgress
      );
      const callArgs = api.post.mock.calls[0];
      const formData = callArgs[1];
      expect(formData.get('name')).toMatch(/^Sample_\d+$/);
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(
        voiceCloneService.uploadVoiceSample(mockFile, 'Test Sample', mockOnProgress)
      ).rejects.toThrow('No authentication token found');
      expect(api.post).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'File upload failed',
          },
        },
      };
      api.post.mockRejectedValue(mockError);
      await expect(
        voiceCloneService.uploadVoiceSample(mockFile, 'Test Sample', mockOnProgress)
      ).rejects.toBe('File upload failed');
    });

    test('Throws generic error when API request fails without response data', async () => {
      const mockError = new Error('Network error');
      api.post.mockRejectedValue(mockError);
      await expect(
        voiceCloneService.uploadVoiceSample(mockFile, 'Test Sample', mockOnProgress)
      ).rejects.toBe(mockError);
    });
  });

  /*
   * Test cases for createVoiceClone.
   */
  describe('createVoiceClone', () => {
    const mockCloneData = {
      name: 'My Voice Clone',
      sample_ids: [1, 2, 3],
      description: 'Test clone',
    };

    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          id: 1,
          name: 'My Voice Clone',
          status: 'processing',
          created_at: '2025-01-01T00:00:00Z',
        },
      },
    };

    test('Successfully creates voice clone', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.createVoiceClone(mockCloneData);
      expect(api.post).toHaveBeenCalledWith('/voice/clones', mockCloneData, {
        headers: {
          Authorization: 'Bearer mock_access_token',
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(
        voiceCloneService.createVoiceClone(mockCloneData)
      ).rejects.toThrow('No authentication token found');
      expect(api.post).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Clone creation failed',
          },
        },
      };
      api.post.mockRejectedValue(mockError);
      await expect(
        voiceCloneService.createVoiceClone(mockCloneData)
      ).rejects.toBe('Clone creation failed');
    });
  });

  /*
   * Test cases for listVoiceClones.
   */
  describe('listVoiceClones', () => {
    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          clones: [
            { id: 1, name: 'Clone 1', status: 'ready' },
            { id: 2, name: 'Clone 2', status: 'processing' },
          ],
          total: 2,
          page: 1,
          page_size: 20,
        },
      },
    };

    test('Successfully lists voice clones with default pagination', async () => {
      api.get.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.listVoiceClones();
      expect(api.get).toHaveBeenCalledWith('/voice/clones', {
        params: { page: 1, page_size: 20 },
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Successfully lists voice clones with custom pagination', async () => {
      api.get.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.listVoiceClones(2, 10);
      expect(api.get).toHaveBeenCalledWith('/voice/clones', {
        params: { page: 2, page_size: 10 },
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(voiceCloneService.listVoiceClones()).rejects.toThrow(
        'No authentication token found'
      );
      expect(api.get).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: { error: 'Failed to fetch clones' },
        },
      };
      api.get.mockRejectedValue(mockError);
      await expect(voiceCloneService.listVoiceClones()).rejects.toBe(
        'Failed to fetch clones'
      );
    });
  });

  /*
   * Test cases for getVoiceClone.
   */
  describe('getVoiceClone', () => {
    const mockCloneId = 123;
    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          id: 123,
          name: 'Test Clone',
          status: 'ready',
          created_at: '2025-01-01T00:00:00Z',
          samples: [1, 2, 3],
        },
      },
    };

    test('Successfully gets voice clone by ID', async () => {
      api.get.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.getVoiceClone(mockCloneId);
      expect(api.get).toHaveBeenCalledWith(`/voice/clones/${mockCloneId}`, {
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(voiceCloneService.getVoiceClone(mockCloneId)).rejects.toThrow(
        'No authentication token found'
      );
      expect(api.get).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Clone not found',
          },
        },
      };
      api.get.mockRejectedValue(mockError);
      await expect(voiceCloneService.getVoiceClone(mockCloneId)).rejects.toBe(
        'Clone not found'
      );
    });
  });

  /*
   * Test cases for deleteVoiceClone.
   */
  describe('deleteVoiceClone', () => {
    const mockCloneId = 123;
    const mockSuccessResponse = {
      data: {
        success: true,
        message: 'Clone deleted successfully',
      },
    };

    test('Successfully deletes voice clone', async () => {
      api.delete.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.deleteVoiceClone(mockCloneId);
      expect(api.delete).toHaveBeenCalledWith(`/voice/clones/${mockCloneId}`, {
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(
        voiceCloneService.deleteVoiceClone(mockCloneId)
      ).rejects.toThrow('No authentication token found');
      expect(api.delete).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: { error: 'Failed to delete clone' }
        },
      };
      api.delete.mockRejectedValue(mockError);
      await expect(
        voiceCloneService.deleteVoiceClone(mockCloneId)
      ).rejects.toBe('Failed to delete clone');
    });
  });

  /*
   * Test cases for selectVoiceClone.
   */
  describe('selectVoiceClone', () => {
    const mockCloneId = 123;
    const mockSuccessResponse = {
      data: {
        success: true,
        message: 'Clone selected successfully',
      },
    };

    test('Successfully selects voice clone', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.selectVoiceClone(mockCloneId);
      expect(api.post).toHaveBeenCalledWith(
        `/voice/clones/${mockCloneId}/select`,
        {},
        {
          headers: {
            Authorization: 'Bearer mock_access_token',
          },
        }
      );
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(
        voiceCloneService.selectVoiceClone(mockCloneId)
      ).rejects.toThrow('No authentication token found');
      expect(api.post).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Failed to select clone',
          },
        },
      };
      api.post.mockRejectedValue(mockError);
      await expect(
        voiceCloneService.selectVoiceClone(mockCloneId)
      ).rejects.toBe('Failed to select clone');
    });
  });

  /*
   * Test cases for synthesizeWithClone.
   */
  describe('synthesizeWithClone', () => {
    const mockCloneId = 123;
    const mockText = 'Hello, this is a test synthesis.';
    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          audio_url: '/path/to/synthesized/audio.wav',
          text: mockText,
          duration: 5.2,
        },
      },
    };

    test('Successfully synthesizes with clone using default config', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.synthesizeWithClone(
        mockCloneId,
        mockText
      );

      expect(api.post).toHaveBeenCalledWith(
        `/voice/clones/${mockCloneId}/synthesize`,
        {
          text: mockText,
          language: 'zh-CN',
          output_format: 'wav',
          sample_rate: 22050,
        },
        {
          headers: {
            Authorization: 'Bearer mock_access_token',
            'Content-Type': 'application/json',
          },
        }
      );
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Successfully synthesizes with clone using custom config', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const customConfig = {
        language: 'en-US',
        outputFormat: 'mp3',
        sampleRate: 44100,
      };

      const result = await voiceCloneService.synthesizeWithClone(
        mockCloneId,
        mockText,
        customConfig
      );

      expect(api.post).toHaveBeenCalledWith(
        `/voice/clones/${mockCloneId}/synthesize`,
        {
          text: mockText,
          language: 'en-US',
          output_format: 'mp3',
          sample_rate: 44100,
        },
        {
          headers: {
            Authorization: 'Bearer mock_access_token',
            'Content-Type': 'application/json',
          },
        }
      );
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(
        voiceCloneService.synthesizeWithClone(mockCloneId, mockText)
      ).rejects.toThrow('No authentication token found');
      expect(api.post).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Synthesis failed',
          },
        },
      };
      api.post.mockRejectedValue(mockError);
      await expect(
        voiceCloneService.synthesizeWithClone(mockCloneId, mockText)
      ).rejects.toBe('Synthesis failed');
    });
  });

  /*
   * Test cases for listVoiceSamples.
   */
  describe('listVoiceSamples', () => {
    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          samples: [
            { id: 1, name: 'Sample 1', file_path: '/path1.wav' },
            { id: 2, name: 'Sample 2', file_path: '/path2.wav' },
          ],
          total: 2,
          page: 1,
          page_size: 20,
        },
      },
    };

    test('Successfully lists voice samples with default pagination', async () => {
      api.get.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.listVoiceSamples();
      expect(api.get).toHaveBeenCalledWith('/voice/samples', {
        params: { page: 1, page_size: 20 },
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Successfully lists voice samples with custom pagination', async () => {
      api.get.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.listVoiceSamples(3, 5);
      expect(api.get).toHaveBeenCalledWith('/voice/samples', {
        params: { page: 3, page_size: 5 },
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(voiceCloneService.listVoiceSamples()).rejects.toThrow(
        'No authentication token found'
      );
      expect(api.get).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Failed to fetch samples',
          },
        },
      };
      api.get.mockRejectedValue(mockError);
      await expect(voiceCloneService.listVoiceSamples()).rejects.toBe(
        'Failed to fetch samples'
      );
    });
  });

  /*
   * Test cases for deleteVoiceSample.
   */
  describe('deleteVoiceSample', () => {
    const mockSampleId = 456;
    const mockSuccessResponse = {
      data: {
        success: true,
        message: 'Sample deleted successfully',
      },
    };

    test('Successfully deletes voice sample', async () => {
      api.delete.mockResolvedValue(mockSuccessResponse);
      const result = await voiceCloneService.deleteVoiceSample(mockSampleId);
      expect(api.delete).toHaveBeenCalledWith(`/voice/samples/${mockSampleId}`, {
        headers: {
          Authorization: 'Bearer mock_access_token',
        },
      });
      expect(result).toEqual(mockSuccessResponse.data);
    });

    test('Throws error when no authentication token found', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      await expect(
        voiceCloneService.deleteVoiceSample(mockSampleId)
      ).rejects.toThrow('No authentication token found');
      expect(api.delete).not.toHaveBeenCalled();
    });

    test('Throws error when API request fails', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Failed to delete sample',
          },
        },
      };
      api.delete.mockRejectedValue(mockError);
      await expect(
        voiceCloneService.deleteVoiceSample(mockSampleId)
      ).rejects.toBe('Failed to delete sample');
    });
  });
});
