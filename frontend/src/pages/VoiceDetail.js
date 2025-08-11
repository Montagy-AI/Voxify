import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import voiceCloneService from '../services/voiceClone.service';

const VoiceDetail = () => {
  const { cloneId } = useParams();
  const navigate = useNavigate();
  const [voiceClone, setVoiceClone] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadVoiceClone = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Get detailed voice clone information
        const response = await voiceCloneService.getVoiceClone(cloneId);
        if (response.success) {
          setVoiceClone(response.data);
        } else {
          setError('Failed to load voice clone details');
        }
      } catch (err) {
        console.error('Failed to load voice clone:', err);
        setError('Failed to load voice clone details');
      } finally {
        setLoading(false);
      }
    };

    if (cloneId) {
      loadVoiceClone();
    }
  }, [cloneId]);

  const handleGenerateTTS = () => {
    // Navigate to TTS page with pre-selected voice clone
    navigate(`/tasks/text-to-speech?voice=${cloneId}`);
  };

  const handleDeleteClone = async () => {
    const confirmed = window.confirm(
      `Are you sure you want to delete the voice clone "${voiceClone.name}"? This action cannot be undone.`
    );
    
    if (!confirmed) return;
    
    try {
      await voiceCloneService.deleteVoiceClone(cloneId);
      alert('Voice clone deleted successfully!');
      navigate('/voices');
    } catch (error) {
      console.error('Failed to delete voice clone:', error);
      alert(`Failed to delete voice clone: ${error.message || error}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'ready':
        return 'text-green-400';
      case 'processing':
        return 'text-yellow-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getDisplayStatus = (status) => {
    switch (status?.toLowerCase()) {
      case 'ready':
        return 'Ready';
      case 'processing':
        return 'Processing';
      case 'failed':
        return 'Failed';
      default:
        return status || 'Unknown';
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="flex flex-col items-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
              <p className="text-gray-300">Loading voice clone details...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !voiceClone) {
    return (
      <div className="min-h-screen bg-black text-white p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="mb-4">
                <svg className="w-16 h-16 text-gray-600 mx-auto" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-gray-300 mb-2">
                {error || 'Voice clone not found'}
              </h2>
              <p className="text-gray-400 mb-6">
                The voice clone you're looking for doesn't exist or has been removed.
              </p>
              <button
                onClick={() => navigate('/voices')}
                className="px-6 py-3 bg-white text-black rounded hover:bg-gray-200 transition-colors"
              >
                Back to Voices
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/voices')}
              className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
              title="Back to Voices"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-4xl font-bold">Voice Clone Details</h1>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 text-sm bg-zinc-800 text-gray-300 rounded">
              {voiceClone.language || 'zh-CN'}
            </span>
            <span className={`px-3 py-1 text-sm rounded ${getStatusColor(voiceClone.status)} bg-zinc-800`}>
              {getDisplayStatus(voiceClone.status)}
            </span>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Basic Information</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Name</label>
                  <p className="text-xl text-white">{voiceClone.name || 'Unnamed Voice'}</p>
                </div>
                
                {voiceClone.description && (
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Description</label>
                    <p className="text-gray-300">{voiceClone.description}</p>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Language</label>
                  <p className="text-white">{voiceClone.language || 'zh-CN'}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Status</label>
                  <p className={getStatusColor(voiceClone.status)}>
                    {getDisplayStatus(voiceClone.status)}
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Clone Type</label>
                  <p className="text-white">
                    {voiceClone.clone_type === 'record' ? 'In-App Record' : 'Uploaded Sample'}
                  </p>
                </div>
              </div>
            </div>

            {/* Reference Text */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Reference Text</h2>
              <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4">
                <p className="text-gray-300 leading-relaxed">
                  {voiceClone.ref_text || 'No reference text available'}
                </p>
              </div>
              <p className="text-sm text-gray-400 mt-2">
                This is the text that was spoken in the original voice sample
              </p>
            </div>

            {/* Technical Details */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Technical Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Recording Format</label>
                  <p className="text-white">WAV Audio</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Sample Rate</label>
                  <p className="text-white">44.1 kHz</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Channels</label>
                  <p className="text-white">Mono</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Bit Depth</label>
                  <p className="text-white">16-bit</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Actions & Metadata */}
          <div className="space-y-6">
            {/* Creation Info */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Creation Details</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Created At</label>
                  <p className="text-white text-sm">
                    {formatDate(voiceClone.created_at)}
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Clone ID</label>
                  <p className="text-gray-300 text-sm font-mono break-all">
                    {voiceClone.clone_id}
                  </p>
                </div>
              </div>
            </div>

            {/* Action Button */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Generate Speech</h3>
              
              <button
                onClick={handleGenerateTTS}
                className="w-full px-6 py-3 rounded text-center font-semibold border-2 border-white text-white hover:bg-white hover:text-black transition-colors"
              >
                Generate TTS using this voice clone
              </button>
            </div>

            {/* Quick Actions */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/voices')}
                  className="w-full px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded transition-colors text-sm"
                >
                  Back to All Voices
                </button>
                
                <button
                  onClick={() => navigate('/tasks/voice-clone')}
                  className="w-full px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded transition-colors text-sm"
                >
                  Create New Voice Clone
                </button>
                
                <button
                  onClick={handleDeleteClone}
                  className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors text-sm"
                >
                  Delete Voice Clone
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceDetail;