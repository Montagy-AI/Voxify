import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/auth.service';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordRequirements, setShowPasswordRequirements] =
    useState(false);

  useEffect(() => {
    if (authService.isAuthenticated()) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);

    try {
      const result = await authService.register({
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
      });

      if (result.success) {
        // After successful registration, log the user in
        const loginResult = await authService.login(
          formData.email,
          formData.password
        );
        if (loginResult.success) {
          navigate('/dashboard');
        } else {
          navigate('/login');
        }
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Password validation checks
  const passwordValidations = [
    {
      id: 1,
      text: 'At least 8 characters',
      isValid: formData.password.length >= 8,
    },
    {
      id: 2,
      text: 'Contains at least one number',
      isValid: /\d/.test(formData.password),
    },
    {
      id: 3,
      text: 'Contains at least one special character',
      isValid: /[!@#$%^&*(),.?":{}|<>]/.test(formData.password),
    },
    {
      id: 4,
      text: 'Contains at least one uppercase letter',
      isValid: /[A-Z]/.test(formData.password),
    },
    {
      id: 5,
      text: 'Contains at least one lowercase letter',
      isValid: /[a-z]/.test(formData.password),
    },
  ];

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <Link to="/" className="inline-block mb-8">
              <img
                src="/logo.png"
                alt="Voxify Logo"
                className="h-12 w-auto mx-auto"
              />
            </Link>
            <h2 className="text-3xl font-bold tracking-tight text-white">
              Create your account
            </h2>
          </div>

          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              {/* First Name */}
              <div>
                <label
                  htmlFor="firstName"
                  className="block text-sm font-medium text-gray-300"
                >
                  First Name
                </label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded border border-zinc-800 bg-zinc-900 px-3 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  placeholder="Enter your first name"
                  disabled={isLoading}
                />
              </div>

              {/* Last Name */}
              <div>
                <label
                  htmlFor="lastName"
                  className="block text-sm font-medium text-gray-300"
                >
                  Last Name
                </label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded border border-zinc-800 bg-zinc-900 px-3 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  placeholder="Enter your last name"
                  disabled={isLoading}
                />
              </div>

              {/* Email */}
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-300"
                >
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded border border-zinc-800 bg-zinc-900 px-3 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  placeholder="Enter your email"
                  disabled={isLoading}
                />
              </div>

              {/* Password */}
              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-gray-300"
                >
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    value={formData.password}
                    onChange={handleChange}
                    onFocus={() => setShowPasswordRequirements(true)}
                    onBlur={() => {
                      if (!formData.password) {
                        setShowPasswordRequirements(false);
                      }
                    }}
                    className="mt-1 block w-full rounded border border-zinc-800 bg-zinc-900 px-3 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors pr-10"
                    placeholder="Create a password"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    className="absolute inset-y-0 right-0 mt-1 flex items-center pr-3 text-gray-400 hover:text-white"
                  >
                    {showPassword ? (
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="w-5 h-5"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                      </svg>
                    ) : (
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="w-5 h-5"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
                        />
                      </svg>
                    )}
                  </button>
                </div>

                {/* Password Requirements */}
                {(showPasswordRequirements || formData.password) && (
                  <div className="mt-2 p-3 bg-zinc-900 border border-zinc-800 rounded text-sm">
                    <p className="text-gray-300 mb-2">Password must contain:</p>
                    <ul className="space-y-1">
                      {passwordValidations.map((validation) => (
                        <li key={validation.id} className="flex items-center">
                          <span
                            className={`inline-block w-4 h-4 mr-2 ${validation.isValid ? 'text-green-500' : 'text-gray-500'}`}
                          >
                            {validation.isValid ? (
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                                  clipRule="evenodd"
                                />
                              </svg>
                            ) : (
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                              >
                                <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                              </svg>
                            )}
                          </span>
                          <span
                            className={
                              validation.isValid
                                ? 'text-gray-300'
                                : 'text-gray-500'
                            }
                          >
                            {validation.text}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label
                  htmlFor="confirmPassword"
                  className="block text-sm font-medium text-gray-300"
                >
                  Confirm Password
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded border border-zinc-800 bg-zinc-900 px-3 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors pr-10"
                    placeholder="Confirm your password"
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>

            {error && (
              <div className="text-red-500 text-sm text-center bg-red-500/10 py-2 rounded">
                {error}
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className={`group relative flex w-full justify-center rounded border-2 border-white bg-transparent px-3 py-2 text-sm font-semibold text-white hover:bg-white hover:text-black transition-colors focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black ${
                  isLoading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isLoading ? (
                  <span className="flex items-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Creating account...
                  </span>
                ) : (
                  'Create account'
                )}
              </button>
            </div>

            <div className="text-center text-sm">
              <div className="text-gray-400 mb-2">Already have an account?</div>
              <Link
                to="/login"
                className="inline-block w-full rounded bg-white px-3 py-2 text-sm font-semibold text-black hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black"
              >
                Log in
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
