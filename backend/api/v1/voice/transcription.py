"""
Voice Transcription Service
Uses OpenAI Whisper API to convert audio to text
"""

import os
from openai import OpenAI, AuthenticationError, RateLimitError, APIError
from typing import Optional
import tempfile
from pathlib import Path

class TranscriptionService:
    """Service for transcribing audio files using OpenAI Whisper API"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
    
    def transcribe_audio(self, audio_file_path: str, language: str = None) -> dict:
        """
        Transcribe audio file to text using OpenAI Whisper API
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file to transcribe
        language : str, optional
            Language code (e.g., 'zh', 'en') for better accuracy
            
        Returns
        -------
        dict
            Dictionary containing:
            - success: bool
            - text: str (transcribed text)
            - language: str (detected language)
            - error: str (if failed)
        """
        try:
            # Check if API key is configured
            if not self.client:
                return {
                    'success': False,
                    'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'
                }
            
            # Check if file exists
            if not os.path.exists(audio_file_path):
                return {
                    'success': False,
                    'error': f'Audio file not found: {audio_file_path}'
                }
            
            # Check file size (OpenAI has 25MB limit)
            file_size = os.path.getsize(audio_file_path)
            if file_size > 25 * 1024 * 1024:  # 25MB in bytes
                return {
                    'success': False,
                    'error': 'Audio file too large. OpenAI Whisper API has a 25MB limit.'
                }
            
            print(f"[TRANSCRIPTION] Starting transcription for: {audio_file_path}")
            print(f"[TRANSCRIPTION] File size: {file_size / 1024 / 1024:.2f}MB")
            
            # Open and transcribe the audio file
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language else None,
                    response_format="verbose_json"
                )
            
            print(f"[TRANSCRIPTION] Successfully transcribed audio")
            print(f"[TRANSCRIPTION] Detected language: {transcript.language}")
            print(f"[TRANSCRIPTION] Text: {transcript.text[:100]}...")
            
            return {
                'success': True,
                'text': transcript.text.strip(),
                'language': transcript.language,
                'duration': getattr(transcript, 'duration', None)
            }
            
        except AuthenticationError:
            return {
                'success': False,
                'error': 'Invalid OpenAI API key. Please check your OPENAI_API_KEY.'
            }
        except RateLimitError:
            return {
                'success': False,
                'error': 'OpenAI API rate limit exceeded. Please try again later.'
            }
        except APIError as e:
            return {
                'success': False,
                'error': f'OpenAI API error: {str(e)}'
            }
        except Exception as e:
            print(f"[TRANSCRIPTION] Error: {str(e)}")
            return {
                'success': False,
                'error': f'Transcription failed: {str(e)}'
            }
    
    def is_configured(self) -> bool:
        """Check if the transcription service is properly configured"""
        return self.client is not None

# Global instance
transcription_service = TranscriptionService() 