import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/auth.service';

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Redirect to dashboard if already authenticated
    if (authService.isAuthenticated()) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    // Basic email validation
    if (!email) {
      setError('Email is required');
      setIsLoading(false);
      return;
    }

    if (!email.includes('@')) {
      setError('Please enter a valid email address');
      setIsLoading(false);
      return;
    }

    try {
      const result = await authService.forgotPassword(email);

      if (result.success) {
        setSuccess(
          result.message ||
            'If an account with that email exists, a password reset link has been sent.'
        );
        setEmail(''); // Clear the form
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to send reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <Link to="/" className="inline-block mb-8">
              <img
                src="/logo.png"
                alt="Voxify"
                className="mx-auto h-12 w-auto"
              />
            </Link>
            <h2 className="text-3xl font-bold tracking-tight">
              Forgot your password?
            </h2>
            <p className="mt-2 text-sm text-gray-400">
              Enter your email address and we'll send you a link to reset your
              password.
            </p>
          </div>

          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
  
                className="relative block w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white placeholder-gray-400 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
              />
            </div>

            {error && (
              <div className="rounded-md bg-red-900/50 border border-red-700 p-3">
                <p className="text-sm text-red-200">{error}</p>
              </div>
            )}

            {success && (
              <div className="rounded-md bg-green-900/50 border border-green-700 p-3">
                <p className="text-sm text-green-200">{success}</p>
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative flex w-full justify-center rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      role="status"
                      aria-label="Loading"
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
                    Sending...
                  </div>
                ) : (
                  'Send Reset Link'
                )}
              </button>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-400">
                Remember your password?{' '}
                <Link
                  to="/login"
                  className="font-medium text-blue-400 hover:text-blue-300"
                >
                  Sign in
                </Link>
              </p>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-400">
                Don't have an account?{' '}
                <Link
                  to="/register"
                  className="font-medium text-blue-400 hover:text-blue-300"
                >
                  Sign up
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
