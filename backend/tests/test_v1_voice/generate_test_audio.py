#!/usr/bin/env python3
"""
Generate 10 different test audio files for voice testing
"""

import os
import numpy as np
import wave
import struct
import random
from pathlib import Path

def generate_sine_wave(frequency, duration, sample_rate=22050, amplitude=0.3):
    """Generate a sine wave with given frequency and duration"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_data

def generate_voice_like_audio(duration=5.0, sample_rate=22050):
    """Generate voice-like audio with varying frequencies"""
    # Create a more complex waveform that sounds more like voice
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Base frequency (around human voice range)
    base_freq = random.uniform(150, 300)
    
    # Create a complex waveform with harmonics
    wave_data = np.zeros_like(t)
    
    # Add fundamental frequency
    wave_data += 0.3 * np.sin(2 * np.pi * base_freq * t)
    
    # Add harmonics
    for i in range(2, 5):
        wave_data += 0.1 * np.sin(2 * np.pi * base_freq * i * t)
    
    # Add some variation over time
    envelope = np.exp(-t / duration) * (1 + 0.5 * np.sin(2 * np.pi * 0.5 * t))
    wave_data *= envelope
    
    # Add some noise to make it more realistic
    noise = np.random.normal(0, 0.01, len(wave_data))
    wave_data += noise
    
    return wave_data

def create_wav_file(filename, audio_data, sample_rate=22050):
    """Create a WAV file from audio data"""
    # Convert Path object to string
    filename_str = str(filename)
    
    with wave.open(filename_str, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Convert to 16-bit integers
        audio_int = (audio_data * 32767).astype(np.int16)
        
        # Write audio data
        wav_file.writeframes(audio_int.tobytes())

def generate_test_audio_files():
    """Generate 10 different test audio files"""
    output_dir = Path(__file__).parent
    sample_rate = 22050
    
    # Different durations for variety
    durations = [3.0, 4.0, 5.0, 6.0, 7.0, 4.5, 5.5, 6.5, 3.5, 4.8]
    
    print("Generating 10 test audio files...")
    
    for i in range(1, 11):
        filename = output_dir / f"test_audio_{i}.wav"
        
        # Generate unique voice-like audio
        duration = durations[i-1]
        audio_data = generate_voice_like_audio(duration, sample_rate)
        
        # Create WAV file
        create_wav_file(filename, audio_data, sample_rate)
        
        print(f"Generated: {filename} ({duration:.1f}s)")
    
    print("\nAll test audio files generated successfully!")
    print("Files created:")
    for i in range(1, 11):
        filename = output_dir / f"test_audio_{i}.wav"
        if filename.exists():
            size = filename.stat().st_size / 1024  # KB
            print(f"  test_audio_{i}.wav ({size:.1f} KB)")

if __name__ == "__main__":
    generate_test_audio_files() 