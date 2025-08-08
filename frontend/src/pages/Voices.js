import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/auth.service';
import apiConfig from '../config/api.config';

const Voices = () => {
  const navigate = useNavigate();
  const [clones, setClones] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchVoiceClones = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`${apiConfig.apiBaseUrl}/voice/clones`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch voice clones');
      }

      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error || 'Unknown error');
      }

      setClones(data.data.clones || []);
      setError('');
    } catch (err) {
      setError(err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    const init = async () => {
      const user = authService.getCurrentUser();
      if (!user || !authService.isAuthenticated()) {
        navigate('/login');
        return;
      }

      await fetchVoiceClones();
    };

    init();
  }, [fetchVoiceClones, navigate]);

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'text-green-500';
      case 'training':
        return 'text-yellow-500';
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-gray-400';
    }
  };

  const getDisplayStatus = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'Ready';
      default:
        return status;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-12">Voice Clones</h1>

        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-white" role="status" aria-label="Loading"></div>
          </div>
        ) : error ? (
          <div className="text-red-500 text-center bg-red-500/10 py-4 rounded border border-red-500/20">
            {error}
          </div>
        ) : clones.length === 0 ? (
          <div className="text-center py-12 bg-zinc-900 rounded-lg border border-zinc-800">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              role="img"
              aria-label="No voice clones"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 17v-6a2 2 0 012-2h2a2 2 0 012 2v6m4 0V9a4 4 0 00-4-4H9a4 4 0 00-4 4v8"
              />
            </svg>
            <p className="text-gray-400 text-lg mt-4">No voice clones found</p>
            <p className="text-gray-500 text-sm mt-2">
              You can create your first voice clone using the Dashboard
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {clones.map((clone) => (
              <div
                key={clone.clone_id}
                className="group bg-zinc-900 rounded-lg p-6 hover:bg-zinc-800 transition-colors border border-zinc-800 cursor-pointer relative"
                onClick={() => navigate('/tasks/text-to-speech/')}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 text-xs bg-zinc-800 text-gray-300 rounded">
                        {clone.language || 'zh-CN'}
                      </span>
                      <span
                        className={`${getStatusColor(clone.status)} capitalize`}
                      >
                        {getDisplayStatus(clone.status)}
                      </span>
                    </div>
                    <h3 className="text-xl font-semibold mb-2 line-clamp-2 break-words">
                      {clone.name || 'Unnamed Voice'}
                    </h3>
                  </div>
                  <button>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className={`w-5 h-5 ${
                        clone.status?.toLowerCase() === 'completed'
                          ? 'text-white group-hover:translate-x-1 transition-transform'
                          : 'text-zinc-500'
                      }`}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M8.25 4.5l7.5 7.5-7.5 7.5"
                      />
                    </svg>
                  </button>
                </div>
                <p className="text-gray-400 text-sm mb-1">
                  {clone.description || 'No description provided.'}
                </p>
                <p className="text-gray-500 text-xs">
                  Created: {formatDate(clone.created_at)}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Voices;
