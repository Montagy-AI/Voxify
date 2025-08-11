import React, { useState, useRef, useEffect } from 'react';
import { convertToWAV } from '../utils/audioConverter';

const VoiceRecorder = ({ randomScript, onRecordingComplete, language }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioDevices, setAudioDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [isLoadingDevices, setIsLoadingDevices] = useState(true);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const audioRef = useRef(null);

  // Load available audio devices
  useEffect(() => {
    const loadAudioDevices = async () => {
      try {
        // Request permission first
        await navigator.mediaDevices.getUserMedia({ audio: true });
        
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(device => device.kind === 'audioinput');
        
        setAudioDevices(audioInputs);
        
        // Set default device if none selected
        if (audioInputs.length > 0 && !selectedDeviceId) {
          setSelectedDeviceId(audioInputs[0].deviceId);
        }
      } catch (error) {
        console.error('Failed to load audio devices:', error);
      } finally {
        setIsLoadingDevices(false);
      }
    };

    loadAudioDevices();
  }, [selectedDeviceId]);

  // Clean up timer
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Start recording
  const startRecording = async () => {
    try {
      const constraints = {
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      };

      // Use selected device if available
      if (selectedDeviceId) {
        constraints.audio.deviceId = { exact: selectedDeviceId };
      }

      const stream = await navigator.mediaDevices.getUserMedia(constraints);

      // Use webm format for recording, will convert to WAV later
      const mimeType = 'audio/webm;codecs=opus';
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: mimeType
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const webmBlob = new Blob(audioChunksRef.current, { 
          type: mimeType 
        });
        
        try {
          // Convert to WAV format
          const wavBlob = await convertToWAV(webmBlob);
          
          // Create audio URL for preview (use original webm for better browser compatibility)
          const audioUrl = URL.createObjectURL(webmBlob);
          setRecordedAudio(audioUrl);

          // Create WAV File object to pass to parent component
          const audioFile = new File([wavBlob], `recording_${Date.now()}.wav`, {
            type: 'audio/wav'
          });

          onRecordingComplete(audioFile);
        } catch (error) {
          console.error('Failed to convert to WAV:', error);
          // Fallback to original format
          const audioUrl = URL.createObjectURL(webmBlob);
          setRecordedAudio(audioUrl);
          
          const audioFile = new File([webmBlob], `recording_${Date.now()}.webm`, {
            type: mimeType
          });
          
          onRecordingComplete(audioFile);
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      setIsRecording(true);
      setRecordingDuration(0);
      mediaRecorder.start();

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Unable to access microphone. Please ensure microphone permissions are granted.');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // Play/pause recording
  const togglePlayback = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  // Re-record
  const resetRecording = () => {
    if (recordedAudio) {
      URL.revokeObjectURL(recordedAudio);
      setRecordedAudio(null);
    }
    setRecordingDuration(0);
    onRecordingComplete(null);
  };

  // Format time display
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* Random script display */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-300 mb-3">
          Please read the following text:
        </h3>
        <p className="text-white text-lg leading-relaxed bg-zinc-800 p-4 rounded border-l-4 border-white">
          {randomScript}
        </p>
        <p className="text-gray-400 text-sm mt-2">
          * Please read clearly with no background noise
        </p>
      </div>

      {/* Microphone selector */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <h4 className="text-md font-medium text-gray-300 mb-3">Microphone Selection</h4>
        {isLoadingDevices ? (
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span className="text-gray-400">Loading devices...</span>
          </div>
        ) : (
          <div className="space-y-2">
            <select
              value={selectedDeviceId}
              onChange={(e) => setSelectedDeviceId(e.target.value)}
              className="w-full rounded border border-zinc-700 bg-zinc-800 px-3 py-2 text-white focus:border-white focus:outline-none focus:ring-1 focus:ring-white transition-colors"
              disabled={isRecording}
            >
              {audioDevices.map((device, index) => (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label && device.label.trim() !== '' && device.label !== 'Default' && device.label !== 'default'
                    ? device.label
                    : `Microphone ${index + 1}`}
                </option>
              ))}
            </select>
            <p className="text-gray-400 text-sm">
              {audioDevices.length === 0 
                ? 'No microphones found' 
                : `${audioDevices.length} microphone(s) available`}
            </p>
          </div>
        )}
      </div>

      {/* Recording control area */}
      <div className="text-center space-y-4">
        {!recordedAudio ? (
          // Recording button and status
          <div className="space-y-4">
            <button
              type="button"
              onClick={isRecording ? stopRecording : startRecording}
              disabled={audioDevices.length === 0 || isLoadingDevices}
              className={`inline-flex items-center justify-center w-20 h-20 rounded-full text-white font-semibold transition-all duration-200 ${
                audioDevices.length === 0 || isLoadingDevices
                  ? 'bg-gray-800 cursor-not-allowed opacity-50'
                  : isRecording
                  ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                  : 'bg-gray-600 hover:bg-gray-700'
              }`}
            >
              {isRecording ? (
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
              ) : (
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  <line x1="12" y1="19" x2="12" y2="23" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <line x1="8" y1="23" x2="16" y2="23" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </button>

            <div>
              <p className="text-gray-300 font-medium">
                {audioDevices.length === 0 
                  ? 'No Microphone' 
                  : isLoadingDevices 
                  ? 'Loading...'
                  : isRecording 
                  ? 'Recording...' 
                  : 'Start Recording'}
              </p>
              {recordingDuration > 0 && (
                <p className="text-gray-400 text-sm mt-1">
                  {formatDuration(recordingDuration)}
                </p>
              )}
            </div>
          </div>
        ) : (
          // Preview and controls after recording completion
          <div className="space-y-4">
            <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-4">
              <div className="flex items-center justify-center space-x-4">
                <button
                  type="button"
                  onClick={togglePlayback}
                  className="w-12 h-12 bg-gray-600 hover:bg-gray-700 rounded-full flex items-center justify-center text-white transition-colors"
                >
                  {isPlaying ? (
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <rect x="6" y="4" width="4" height="16" />
                      <rect x="14" y="4" width="4" height="16" />
                    </svg>
                  ) : (
                    <svg className="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24">
                      <polygon points="5,3 19,12 5,21" />
                    </svg>
                  )}
                </button>
                
                <div className="text-center">
                  <p className="text-white font-medium">Recording Complete</p>
                  <p className="text-gray-400 text-sm">
                    Duration: {formatDuration(recordingDuration)}
                  </p>
                </div>
              </div>

              <div className="flex justify-center space-x-4 mt-4">
                <button
                  type="button"
                  onClick={resetRecording}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded transition-colors"
                >
                  Re-record
                </button>
              </div>
            </div>

            {/* Hidden audio element for playback */}
            <audio
              ref={audioRef}
              src={recordedAudio}
              onEnded={() => setIsPlaying(false)}
              className="hidden"
            />
          </div>
        )}
      </div>

      {/* Recording tips */}
      <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
            <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="text-sm text-gray-300">
            <p className="font-medium mb-1">Recording Tips:</p>
            <ul className="space-y-1 text-gray-300">
              <li>• Record in a quiet environment</li>
              <li>• Speak at normal pace with clear pronunciation</li>
              <li>• Recommended recording length: 10-30 seconds</li>
              <li>• You can preview the recording after completion</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceRecorder;