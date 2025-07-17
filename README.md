This branch will update the following feature:
## 🗣️ Voice Transcription Service (STT Integration)

This module integrates OpenAI's Whisper API to automatically transcribe user-uploaded audio files into text during the voice cloning process in **Voxify**.

### 🔍 Purpose
Previously, users needed to manually enter the reference text for their uploaded voice samples, which was time-consuming and error-prone. With Whisper STT, we now auto-generate accurate transcriptions from `.wav` files, significantly improving usability and reducing friction.

### ⚙️ Features
- Auto transcription of uploaded `.wav` audio files using OpenAI Whisper (`whisper-1`)
- Frontend UI integration with editable transcription field
- File validation and error handling
- Language detection and audio duration metadata
- Environment-independent configuration for portability

### 🏗️ Technical Architecture
- **Backend**: Python class-based service wrapping OpenAI Whisper API, located at:
  ```python
  backend/api/v1/voice/transcription.py
  ```
- **Frontend**: Displays detected transcription and allows minor edits
- **API Integration**: Uses ```client.audio.transcriptions.create()``` with ```verbose_json``` for language and duration detection

### 🚀 Quickstart
- **1. Install Dependencies**: 
```pip install openai>=1.30.0```
- **2. Set Up Environment**: ```OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx```
- **3. Verify Configuration**:
```python
python -c "from api.v1.voice.transcription import transcription_service; print(transcription_service.is_configured())"
```
- **4. API Usage**:
```json
{
  "success": true,
  "data": {
    "sample_id": "...",
    "transcription": "Auto-detected speech from audio",
    "transcription_language": "en",
    "duration": 5.2
  }
}
```
### 🧠 Model Used

- **Model**: `whisper-1`
- **File size limit**: 25MB
- **Supported formats**: WAV, MP3, M4A, FLAC, WEBM
- **Language detection**: Automatic (or optionally specified)

---

### 🛠️ Development Summary

The integration was built by:

- Testing Whisper API endpoints via local scripts
- Wrapping API logic into a dedicated Python service class
- Connecting this logic to our Flask backend
- Integrating the result with the frontend UI

---

### ⚠️ Known Limitations

- File size must be under 25MB due to OpenAI API constraints
- Environment mismatches across IDEs required extra setup time
- Accuracy depends on audio clarity and spoken language support

---

### ✅ Impact

- Eliminated the need for manual reference text entry
- Reduced human transcription error
- Maintained runtime efficiency with minimal additional GPU load
