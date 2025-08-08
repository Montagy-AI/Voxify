import authService from '../auth.service';

// Import the mocked api
import api from '../api';

// Mock the api module
jest.mock('../api', () => ({
  post: jest.fn(),
  get: jest.fn(),
  put: jest.fn(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Mock window.location
const mockLocation = {
  href: '',
};

// Setup mocks
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    mockLocation.href = '';
  });

  /*
        Test cases for login.
    */
  describe('login', () => {
    const validCredentials = {
      email: 'test@example.com',
      password: 'password123',
    };

    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          access_token: 'mock_access_token',
          refresh_token: 'mock_refresh_token',
          user: {
            id: 1,
            email: 'test@example.com',
            first_name: 'John',
            last_name: 'Doe',
          },
        },
      },
    };

    test('Successful login stores tokens and user data', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await authService.login(
        validCredentials.email,
        validCredentials.password
      );
      expect(api.post).toHaveBeenCalledWith('/auth/login', validCredentials);
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'access_token',
        'mock_access_token'
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'refresh_token',
        'mock_refresh_token'
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'user',
        JSON.stringify(mockSuccessResponse.data.data.user)
      );
      expect(result).toEqual({
        success: true,
        user: mockSuccessResponse.data.data.user,
      });
    });

    test('Failed login with error message returns error', async () => {
      const mockErrorResponse = {
        data: {
          success: false,
          error: { message: 'Invalid credentials' },
        },
      };
      api.post.mockResolvedValue(mockErrorResponse);
      const result = await authService.login(
        validCredentials.email,
        validCredentials.password
      );
      expect(api.post).toHaveBeenCalledWith('/auth/login', validCredentials);
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
      expect(result).toEqual({
        success: false,
        error: 'Invalid credentials',
      });
    });

    test('Failed login without error message returns default error', async () => {
      const mockErrorResponse = {
        data: { success: false },
      };
      api.post.mockResolvedValue(mockErrorResponse);
      const result = await authService.login(
        validCredentials.email,
        validCredentials.password
      );
      expect(result).toEqual({
        success: false,
        error: 'Login failed',
      });
    });

    test('Network error returns error with message from response', async () => {
      const mockError = {
        response: {
          data: { error: { message: 'Network timeout' } },
        },
      };
      api.post.mockRejectedValue(mockError);
      const result = await authService.login(
        validCredentials.email,
        validCredentials.password
      );
      expect(result).toEqual({
        success: false,
        error: 'Network timeout',
      });
    });

    test('Network error without detailed message returns default error', async () => {
      const mockError = new Error('Network Error');
      api.post.mockRejectedValue(mockError);
      const result = await authService.login(
        validCredentials.email,
        validCredentials.password
      );
      expect(result).toEqual({
        success: false,
        error: 'Login failed',
      });
    });
  });

  /*
        Test cases for registration.
    */
  describe('register', () => {
    const validUserData = {
      email: 'test@example.com',
      password: 'password123',
      firstName: 'John',
      lastName: 'Doe',
    };

    const mockApiPayload = {
      email: 'test@example.com',
      password: 'password123',
      first_name: 'John',
      last_name: 'Doe',
    };

    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          user: {
            id: 1,
            email: 'test@example.com',
            first_name: 'John',
            last_name: 'Doe',
          },
        },
      },
    };

    test('Successful registration returns user data', async () => {
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await authService.register(validUserData);
      expect(api.post).toHaveBeenCalledWith('/auth/register', mockApiPayload);
      expect(result).toEqual({
        success: true,
        user: mockSuccessResponse.data.data.user,
      });
    });

    test('Failed registration with error message returns error', async () => {
      const mockErrorResponse = {
        data: {
          success: false,
          error: { message: 'Email already exists' },
        },
      };
      api.post.mockResolvedValue(mockErrorResponse);
      const result = await authService.register(validUserData);
      expect(result).toEqual({
        success: false,
        error: 'Email already exists',
      });
    });

    test('Failed registration without error message returns default error', async () => {
      const mockErrorResponse = {
        data: { success: false },
      };
      api.post.mockResolvedValue(mockErrorResponse);
      const result = await authService.register(validUserData);
      expect(result).toEqual({
        success: false,
        error: 'Registration failed',
      });
    });

    test('Network error returns error with message from response', async () => {
      const mockError = {
        response: {
          data: {
            error: { message: 'Server unavailable' },
          },
        },
      };
      api.post.mockRejectedValue(mockError);
      const result = await authService.register(validUserData);
      expect(result).toEqual({
        success: false,
        error: 'Server unavailable',
      });
    });

    test('Network error without detailed message returns default error', async () => {
      const mockError = new Error('Network Error');
      api.post.mockRejectedValue(mockError);
      const result = await authService.register(validUserData);
      expect(result).toEqual({
        success: false,
        error: 'Registration failed',
      });
    });
  });

  /*
        Test cases for logout.
    */
  describe('logout', () => {
    test('Remove all tokens and user data from localStorage and redirects', () => {
      authService.logout();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      expect(mockLocation.href).toBe('/login');
    });
  });

  /*
        Test cases for getting the current user.
    */
  describe('getCurrentUser', () => {
    test('Return user data when user exists in localStorage', () => {
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        first_name: 'John',
      };
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockUser));
      const result = authService.getCurrentUser();
      expect(localStorageMock.getItem).toHaveBeenCalledWith('user');
      expect(result).toEqual(mockUser);
    });

    test('Return null when no user data in localStorage', () => {
      localStorageMock.getItem.mockReturnValue(null);
      const result = authService.getCurrentUser();
      expect(result).toBeNull();
    });

    test('Return null when user data is invalid JSON', () => {
      localStorageMock.getItem.mockReturnValue('invalid json');
      const result = authService.getCurrentUser();
      expect(result).toBeNull();
    });

    test('Return null when JSON.parse throws error', () => {
      localStorageMock.getItem.mockReturnValue('{"invalid": json}');
      const result = authService.getCurrentUser();
      expect(result).toBeNull();
    });
  });

  /*
        Test cases for checking authentication status.
    */
  describe('isAuthenticated', () => {
    test('Return true when access token exists', () => {
      localStorageMock.getItem.mockReturnValue('some_token');
      const result = authService.isAuthenticated();
      expect(localStorageMock.getItem).toHaveBeenCalledWith('access_token');
      expect(result).toBe(true);
    });

    test('Return false when access token does not exist', () => {
      localStorageMock.getItem.mockReturnValue(null);
      const result = authService.isAuthenticated();
      expect(result).toBe(false);
    });

    test('Return false when access token is empty string', () => {
      localStorageMock.getItem.mockReturnValue('');
      const result = authService.isAuthenticated();
      expect(result).toBe(false);
    });
  });

  /*
        Test cases for refreshing auth tokens.
    */
  describe('refreshToken', () => {
    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token',
        },
      },
    };

    test('Successful token refresh updates localStorage', async () => {
      localStorageMock.getItem.mockReturnValue('existing_refresh_token');
      api.post.mockResolvedValue(mockSuccessResponse);
      const result = await authService.refreshToken();
      expect(localStorageMock.getItem).toHaveBeenCalledWith('refresh_token');
      expect(api.post).toHaveBeenCalledWith(
        '/auth/refresh',
        {},
        {
          headers: {
            Authorization: 'Bearer existing_refresh_token',
          },
        }
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'access_token',
        'new_access_token'
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'refresh_token',
        'new_refresh_token'
      );
      expect(result).toEqual({ success: true });
    });

    test('Fail when no refresh token available', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      const result = await authService.refreshToken();
      expect(api.post).not.toHaveBeenCalled();
      expect(result).toEqual({
        success: false,
        error: 'Token refresh failed',
      });
    });

    test('Fail refresh with error message returns error', async () => {
      localStorageMock.getItem.mockReturnValue('existing_refresh_token');
      const mockErrorResponse = {
        data: {
          success: false,
          error: { message: 'Refresh token expired' },
        },
      };
      api.post.mockResolvedValue(mockErrorResponse);
      const result = await authService.refreshToken();
      expect(result).toEqual({
        success: false,
        error: 'Refresh token expired',
      });
    });

    test('Network error returns error with message from response', async () => {
      localStorageMock.getItem.mockReturnValue('existing_refresh_token');
      const mockError = {
        response: {
          data: {
            error: { message: 'Unauthorized' },
          },
        },
      };
      api.post.mockRejectedValue(mockError);
      const result = await authService.refreshToken();
      expect(result).toEqual({
        success: false,
        error: 'Unauthorized',
      });
    });

    test('Network error without detailed message returns default error', async () => {
      localStorageMock.getItem.mockReturnValue('existing_refresh_token');
      const mockError = new Error('Network Error');
      api.post.mockRejectedValue(mockError);
      const result = await authService.refreshToken();
      expect(result).toEqual({
        success: false,
        error: 'Token refresh failed',
      });
    });
  });

  /*
        Test cases for getting the user profile.
    */
  describe('getUserProfile', () => {
    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          user: {
            id: 1,
            email: 'test@example.com',
            first_name: 'John',
            last_name: 'Doe',
          },
        },
      },
    };

    test('Successful profile fetch returns user data', async () => {
      api.get.mockResolvedValue(mockSuccessResponse);
      const result = await authService.getUserProfile();
      expect(api.get).toHaveBeenCalledWith('/auth/profile');
      expect(result).toEqual({
        data: mockSuccessResponse.data.data.user,
      });
    });

    test('Throw error when response format is invalid - no success', async () => {
      const mockInvalidResponse = {
        data: {
          data: { user: { id: 1 } },
        },
      };
      api.get.mockResolvedValue(mockInvalidResponse);
      await expect(authService.getUserProfile()).rejects.toThrow(
        'Invalid response format'
      );
    });

    test('Throw error when response format is invalid - no data', async () => {
      const mockInvalidResponse = {
        data: {
          success: true,
        },
      };
      api.get.mockResolvedValue(mockInvalidResponse);
      await expect(authService.getUserProfile()).rejects.toThrow(
        'Invalid response format'
      );
    });

    test('Throw error when response format is invalid - no user', async () => {
      const mockInvalidResponse = {
        data: {
          success: true,
          data: {},
        },
      };
      api.get.mockResolvedValue(mockInvalidResponse);
      await expect(authService.getUserProfile()).rejects.toThrow(
        'Invalid response format'
      );
    });

    test('Network error throws the error', async () => {
      const mockError = new Error('Network Error');
      api.get.mockRejectedValue(mockError);
      await expect(authService.getUserProfile()).rejects.toThrow(
        'Network Error'
      );
    });
  });

  /*
        Test cases for updating the user profile.
    */
  describe('updateUserProfile', () => {
    const mockUserData = {
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane@example.com',
    };

    const mockSuccessResponse = {
      data: {
        success: true,
        data: {
          user: {
            id: 1,
            first_name: 'Jane',
            last_name: 'Smith',
            email: 'jane@example.com',
          },
        },
        message: 'Profile updated successfully',
      },
    };

    test('Successful profile update returns updated user data', async () => {
      api.put.mockResolvedValue(mockSuccessResponse);
      const result = await authService.updateUserProfile(mockUserData);
      expect(api.put).toHaveBeenCalledWith('/auth/profile', mockUserData);
      expect(result).toEqual({
        data: mockSuccessResponse.data.data.user,
        message: mockSuccessResponse.data.message,
      });
    });

    test('Successful profile update with data fallback returns data', async () => {
      const mockResponseWithDataFallback = {
        data: {
          success: true,
          data: {
            id: 1,
            first_name: 'Jane',
            last_name: 'Smith',
          },
          message: 'Profile updated successfully',
        },
      };
      api.put.mockResolvedValue(mockResponseWithDataFallback);
      const result = await authService.updateUserProfile(mockUserData);
      expect(result).toEqual({
        data: mockResponseWithDataFallback.data.data,
        message: mockResponseWithDataFallback.data.message,
      });
    });

    test('Throw error when response format is invalid - no success', async () => {
      const mockInvalidResponse = {
        data: {
          data: { user: { id: 1 } },
        },
      };
      api.put.mockResolvedValue(mockInvalidResponse);
      await expect(authService.updateUserProfile(mockUserData)).rejects.toThrow(
        'Invalid response format'
      );
    });

    test('Throw error when response format is invalid - no data', async () => {
      const mockInvalidResponse = {
        data: {
          success: true,
        },
      };
      api.put.mockResolvedValue(mockInvalidResponse);
      await expect(authService.updateUserProfile(mockUserData)).rejects.toThrow(
        'Invalid response format'
      );
    });

    test('Network error throws the error', async () => {
      const mockError = new Error('Network Error');
      api.put.mockRejectedValue(mockError);
      await expect(authService.updateUserProfile(mockUserData)).rejects.toThrow(
        'Network Error'
      );
    });
  });
});
