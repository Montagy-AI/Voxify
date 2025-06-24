import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const VoiceClone = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(droppedFiles);
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsUploading(true);
    
    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 500);
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-12">Clone your voice</h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Name Input */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
              Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
              placeholder="My voice clone"
            />
          </div>

          {/* Description Input */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
              Description
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors h-32 resize-none"
              placeholder="This is a voice clone of me"
            />
          </div>

          {/* File Upload Section */}
          <div>
            <h2 className="text-xl font-semibold mb-2">Upload voice samples</h2>
            <p className="text-gray-400 mb-4">
              Upload at least 10 minutes of high-quality audio. The more data you provide, the better the clone will be. We recommend 30 minutes or more for optimal results.
            </p>

            {/* Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="border-2 border-dashed border-zinc-800 rounded-lg p-12 text-center hover:border-white transition-colors cursor-pointer"
            >
              <div className="space-y-4">
                <p className="text-lg font-medium">Drag and drop files here</p>
                <p className="text-gray-400">Or click to browse</p>
                <input
                  type="file"
                  multiple
                  accept="audio/*"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <button
                  type="button"
                  onClick={() => document.getElementById('file-upload').click()}
                  className="px-4 py-2 bg-zinc-900 border border-zinc-800 rounded hover:bg-zinc-800 transition-colors"
                >
                  Upload
                </button>
              </div>
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-zinc-900 p-3 rounded">
                    <span className="text-gray-300">{file.name}</span>
                    <span className="text-gray-400">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                  </div>
                ))}
              </div>
            )}

            {/* Upload Progress */}
            {isUploading && (
              <div className="mt-6 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Uploading</span>
                  <span>{uploadProgress}% complete</span>
                </div>
                <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-white transition-all duration-500"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              disabled={!files.length || isUploading}
              className={`w-full px-6 py-3 rounded text-center font-semibold border-2 border-white hover:bg-white hover:text-black transition-colors ${
                (!files.length || isUploading) ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              Create voice clone
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default VoiceClone; 