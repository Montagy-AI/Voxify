import React, { useState } from 'react';
import jobService from '../services/job.service';

const TextToSpeech = () => {
  const [text, setText] = useState('');
  const [voice, setVoice] = useState('');
  const [config, setConfig] = useState({
    speed: 1.0,
    pitch: 1.0,
    volume: 1.0,
    outputFormat: 'wav',
    sampleRate: 22050
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim() || !voice) return;

    setIsGenerating(true);
    
    try {
      // Simulate progress while actually generating
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      await jobService.createSynthesisJob(voice, text, config);
      setProgress(100);
      
      // Reset form after successful generation
      setText('');
      setVoice('');
    } catch (error) {
      console.error('Failed to generate speech:', error);
    } finally {
      setIsGenerating(false);
      setProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-12">Text to Speech</h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Text Input */}
          <div>
            <label htmlFor="text" className="block text-sm font-medium text-gray-300 mb-2">
              Text
            </label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors h-48 resize-none"
              placeholder="Enter the text you want to convert to speech"
              disabled={isGenerating}
            />
          </div>

          {/* Voice Selection */}
          <div>
            <label htmlFor="voice" className="block text-sm font-medium text-gray-300 mb-2">
              Voice
            </label>
            <select
              id="voice"
              value={voice}
              onChange={(e) => setVoice(e.target.value)}
              className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
              disabled={isGenerating}
            >
              <option value="">Select a voice</option>
              <option value="voice1">Voice 1</option>
              <option value="voice2">Voice 2</option>
            </select>
          </div>

          {/* Settings Section */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Settings</h2>
            <div className="space-y-4">
              {/* Speed Control */}
              <div>
                <label htmlFor="speed" className="block text-sm font-medium text-gray-300 mb-2">
                  Speed
                </label>
                <select
                  id="speed"
                  value={config.speed}
                  onChange={(e) => setConfig(prev => ({ ...prev, speed: parseFloat(e.target.value) }))}
                  className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  disabled={isGenerating}
                >
                  <option value="0.75">Slow</option>
                  <option value="1.0">Normal</option>
                  <option value="1.25">Fast</option>
                </select>
              </div>

              {/* Pitch Control */}
              <div>
                <label htmlFor="pitch" className="block text-sm font-medium text-gray-300 mb-2">
                  Pitch
                </label>
                <select
                  id="pitch"
                  value={config.pitch}
                  onChange={(e) => setConfig(prev => ({ ...prev, pitch: parseFloat(e.target.value) }))}
                  className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  disabled={isGenerating}
                >
                  <option value="0.75">Low</option>
                  <option value="1.0">Normal</option>
                  <option value="1.25">High</option>
                </select>
              </div>

              {/* Volume Control */}
              <div>
                <label htmlFor="volume" className="block text-sm font-medium text-gray-300 mb-2">
                  Volume
                </label>
                <select
                  id="volume"
                  value={config.volume}
                  onChange={(e) => setConfig(prev => ({ ...prev, volume: parseFloat(e.target.value) }))}
                  className="w-full rounded border border-zinc-800 bg-zinc-900 px-4 py-2 text-white placeholder-gray-400 focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
                  disabled={isGenerating}
                >
                  <option value="0.75">Quiet</option>
                  <option value="1.0">Normal</option>
                  <option value="1.25">Loud</option>
                </select>
              </div>
            </div>
          </div>

          {/* Generation Progress */}
          {isGenerating && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Generating</span>
                <span>{progress}% complete</span>
              </div>
              <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                <div
                  className="h-full bg-white transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              disabled={!text.trim() || !voice || isGenerating}
              className={`w-full px-6 py-3 rounded text-center font-semibold border-2 border-white hover:bg-white hover:text-black transition-colors ${
                (!text.trim() || !voice || isGenerating) ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isGenerating ? 'Generating...' : 'Generate speech'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TextToSpeech; 