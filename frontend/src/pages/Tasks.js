import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import jobService from '../services/job.service';
import authService from '../services/auth.service';

const Tasks = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const initializePage = async () => {
      // Check if user is logged in
      const currentUser = authService.getCurrentUser();
      const token = localStorage.getItem('access_token');
      
      if (!currentUser || !token) {
        navigate('/login');
        return;
      }

      try {
        // Try to refresh the token first
        if (!authService.isAuthenticated()) {
          const refreshResult = await authService.refreshToken();
          if (!refreshResult.success) {
            navigate('/login');
            return;
          }
        }
        
        // Load jobs after ensuring authentication
        await loadJobs();
      } catch (err) {
        console.error('Error initializing page:', err);
        navigate('/login');
      }
    };

    initializePage();
  }, [navigate]);

  const loadJobs = async () => {
    try {
      const jobsData = await jobService.getSynthesisJobs();
      setJobs(jobsData);
      setError('');
    } catch (err) {
      if (err.message === 'No authentication token found') {
        navigate('/login');
      } else {
        setError('Failed to load synthesis jobs. Please try again later.');
        console.error(err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (jobId) => {
    try {
      const blob = await jobService.downloadSynthesisOutput(jobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `synthesis-${jobId}.wav`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      if (err.message === 'No authentication token found') {
        navigate('/login');
      } else {
        console.error('Failed to download synthesis output:', err);
      }
    }
  };

  const handleCancel = async (jobId) => {
    try {
      await jobService.cancelSynthesisJob(jobId);
      loadJobs(); // Reload jobs list
    } catch (err) {
      if (err.message === 'No authentication token found') {
        navigate('/login');
      } else {
        console.error('Failed to cancel synthesis job:', err);
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'text-green-500';
      case 'processing':
        return 'text-blue-500';
      case 'failed':
        return 'text-red-500';
      case 'pending':
        return 'text-yellow-500';
      default:
        return 'text-gray-500';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-12">Synthesis Tasks</h1>

        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-white"></div>
          </div>
        ) : error ? (
          <div className="text-red-500 text-center bg-red-500/10 py-4 rounded">
            {error}
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-12 bg-zinc-900 rounded-lg border border-zinc-800">
            <p className="text-gray-400">No synthesis tasks found</p>
          </div>
        ) : (
          <div className="space-y-6">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="bg-zinc-900 rounded-lg border border-zinc-800 p-6 hover:border-white transition-colors"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold mb-2 line-clamp-1">
                      {job.text_content}
                    </h3>
                    <p className="text-gray-400 text-sm">
                      Created: {formatDate(job.created_at)}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm ${getStatusColor(job.status)}`}>
                    {job.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div>
                    <p className="text-gray-400">Duration</p>
                    <p>{job.duration ? `${job.duration.toFixed(2)}s` : 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Model</p>
                    <p className="truncate">{job.voice_model?.name || 'Unknown'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Format</p>
                    <p>{job.output_format}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Sample Rate</p>
                    <p>{job.sample_rate} Hz</p>
                  </div>
                </div>

                {/* Progress bar for processing jobs */}
                {job.status === 'processing' && (
                  <div className="mb-4">
                    <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-white transition-all duration-500"
                        style={{ width: `${(job.progress || 0) * 100}%` }}
                      />
                    </div>
                  </div>
                )}

                <div className="flex justify-end space-x-4">
                  {job.status === 'processing' && (
                    <button
                      onClick={() => handleCancel(job.id)}
                      className="px-4 py-2 text-sm border border-red-500 text-red-500 rounded hover:bg-red-500 hover:text-white transition-colors"
                    >
                      Cancel
                    </button>
                  )}
                  {job.status === 'completed' && (
                    <button
                      onClick={() => handleDownload(job.id)}
                      className="px-4 py-2 text-sm border border-white rounded hover:bg-white hover:text-black transition-colors"
                    >
                      Download
                    </button>
                  )}
                </div>

                {job.error_message && (
                  <div className="mt-4 p-3 bg-red-500/10 text-red-500 rounded text-sm">
                    Error: {job.error_message}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Tasks; 