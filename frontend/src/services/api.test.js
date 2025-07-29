// Mock localStorage
const localStorageMock = {
	getItem: jest.fn(),
	setItem: jest.fn(),
	removeItem: jest.fn(),
};

// Mock window.location
const mockLocation = {
	href: '',
};

Object.defineProperty(window, 'localStorage', {
	value: localStorageMock,
});

Object.defineProperty(window, 'location', {
	value: mockLocation,
	writable: true,
});

// Mock authService
jest.mock('./auth.service', () => ({
	default: {
		refreshToken: jest.fn(),
	},
}));

// Mock apiConfig
jest.mock('../config/api.config', () => ({
	default: {
		apiBaseUrl: 'https://api.example.com',
		timeout: 10000,
	},
}));

// Mock axios to avoid interceptor issues
jest.mock('axios', () => ({
	create: jest.fn(() => ({
		defaults: { baseURL: 'https://api.example.com' },
		interceptors: {
			request: { use: jest.fn() },
			response: { use: jest.fn() },
		},
	})),
}));

describe('API Configuration', () => {
	beforeEach(() => {
		jest.clearAllMocks();
		localStorageMock.getItem.mockReturnValue(null);
		mockLocation.href = '';
	});

	describe('Module Loading', () => {
		test('Successfully import api module', () => {
			expect(() => require('./api')).not.toThrow();
		});

		test('API module exports expected functions', () => {
			const apiModule = require('./api');
			expect(apiModule.default).toBeDefined();
			expect(typeof apiModule.createAudioUrl).toBe('function');
		});
	});

	describe('createAudioUrl Helper', () => {
		test('Create synthesis audio URL with token', () => {
			localStorageMock.getItem.mockReturnValue('audio_token');
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl('job123');
			expect(localStorageMock.getItem).toHaveBeenCalledWith('access_token');
			expect(result).toBe('https://api.example.com/file/synthesis/job123?token=audio_token');
		});

		test('Create voice clone audio URL with token', () => {
			localStorageMock.getItem.mockReturnValue('audio_token');
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl('job456', true);
			expect(localStorageMock.getItem).toHaveBeenCalledWith('access_token');
			expect(result).toBe('https://api.example.com/file/voice-clone/job456?token=audio_token');
		});

		test('Create synthesis audio URL when isVoiceClone is false', () => {
			localStorageMock.getItem.mockReturnValue('audio_token');
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl('job789', false);
			expect(result).toBe('https://api.example.com/file/synthesis/job789?token=audio_token');
		});

		test('Create URL with null token when no token in localStorage', () => {
			localStorageMock.getItem.mockReturnValue(null);
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl('job123');
			expect(result).toBe('https://api.example.com/file/synthesis/job123?token=null');
		});

		test('Create URL with empty token when empty string in localStorage', () => {
			localStorageMock.getItem.mockReturnValue('');
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl('job123');
			expect(result).toBe('https://api.example.com/file/synthesis/job123?token=');
		});

		test('Handle different job ID formats', () => {
			localStorageMock.getItem.mockReturnValue('token');
			const { createAudioUrl } = require('./api');
			expect(createAudioUrl('123')).toBe('https://api.example.com/file/synthesis/123?token=token');
			expect(createAudioUrl('abc-123')).toBe('https://api.example.com/file/synthesis/abc-123?token=token');
			expect(createAudioUrl('job_456')).toBe('https://api.example.com/file/synthesis/job_456?token=token');
		});
	});

	describe('Configuration', () => {
		test('Ensure createAudioUrl uses correct base URL', () => {
			localStorageMock.getItem.mockReturnValue('test_token');
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl('job123');
			// Verify it uses the expected base URL from our mock
			expect(result).toContain('https://api.example.com');
		});

		test('Ensure createAudioUrl constructs URLs correctly', () => {
			localStorageMock.getItem.mockReturnValue('token123');
			const { createAudioUrl } = require('./api');
			const synthesisUrl = createAudioUrl('job456');
			const voiceCloneUrl = createAudioUrl('job789', true);
			expect(synthesisUrl).toBe('https://api.example.com/file/synthesis/job456?token=token123');
			expect(voiceCloneUrl).toBe('https://api.example.com/file/voice-clone/job789?token=token123');
		});
	});

	describe('Module Exports', () => {
		test('Export default api instance', () => {
			const api = require('./api').default;
			expect(api).toBeDefined();
		});
		test('Export createAudioUrl function', () => {
			const { createAudioUrl } = require('./api');
			expect(typeof createAudioUrl).toBe('function');
		});
	});

	describe('Edge Cases', () => {
		test('Check createAudioUrl handles undefined jobId', () => {
			localStorageMock.getItem.mockReturnValue('token');
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl(undefined);
			expect(result).toBe('https://api.example.com/file/synthesis/undefined?token=token');
		});

		test('Check createAudioUrl handles null jobId', () => {
			localStorageMock.getItem.mockReturnValue('token');
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl(null);
			expect(result).toBe('https://api.example.com/file/synthesis/null?token=token');
		});

		test('Check createAudioUrl handles empty string jobId', () => {
			localStorageMock.getItem.mockReturnValue('token');
			const { createAudioUrl } = require('./api');
			const result = createAudioUrl('');
			expect(result).toBe('https://api.example.com/file/synthesis/?token=token');
		});
	});

	describe('localStorage Integration', () => {
		test('Check createAudioUrl always calls localStorage.getItem', () => {
			const { createAudioUrl } = require('./api');
			createAudioUrl('test');
			createAudioUrl('test2', true);
			createAudioUrl('test3', false);
			expect(localStorageMock.getItem).toHaveBeenCalledTimes(3);
			expect(localStorageMock.getItem).toHaveBeenCalledWith('access_token');
		});

		test('Check createAudioUrl works with various token values', () => {
			const { createAudioUrl } = require('./api');
			// Test with different token values
			const testCases = [
				{ token: 'simple_token', expected: 'simple_token' },
				{ token: 'Bearer abc123', expected: 'Bearer abc123' },
				{ token: '12345', expected: '12345' },
				{ token: 'token with spaces', expected: 'token with spaces' },
			];
			testCases.forEach(({ token, expected }) => {
				localStorageMock.getItem.mockReturnValue(token);
				const result = createAudioUrl('job123');
				expect(result).toBe(`https://api.example.com/file/synthesis/job123?token=${expected}`);
			});
		});
	});
});