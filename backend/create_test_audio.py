import numpy as np
import soundfile as sf

# Generate a 1-second test tone
sample_rate = 44100
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration), False)
test_tone = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

# Save as WAV file
sf.write('test.wav', test_tone, sample_rate)
print("Test WAV file created: test.wav") 