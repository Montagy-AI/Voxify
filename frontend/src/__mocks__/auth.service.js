const authService = {
  getCurrentUser: jest.fn(() => null),
  isAuthenticated: jest.fn(() => false),
  logout: jest.fn(() => {
    // Mock successful logout
    return Promise.resolve();
  }),
  login: jest.fn((credentials) => {
    // Mock successful login
    return Promise.resolve({
      token: 'mock-token',
      user: { id: 1, email: credentials.email, first_name: 'Test' },
    });
  }),
  register: jest.fn(() => {
    return Promise.resolve({ success: true });
  }),
};

export default authService;
