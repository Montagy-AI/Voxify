# This file was written entirely by Claude AI

import requests
import base64
import json
import os
from datetime import datetime

if __name__ == "__main__":
    print("🚀 Testing F5-TTS Voice Cloning...")
    file = "directory/audio.wav"

    # Read your reference audio file
    try:
        with open(file, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        print("✅ Audio file loaded successfully")
    except FileNotFoundError:
        print("❌ Error: Could not find " + file)
        exit(1)
    except Exception as e:
        print(f"❌ Error reading audio file: {e}")
        exit(1)

    # Make request
    print("📤 Sending request to Modal...")
    try:
        response = requests.post(
            "url_to_your_modal_endpoint/synthesize",
            json={
                "text": "Hello, this is a test of voice cloning. I love cats and cheese.",
                "reference_audio_b64": audio_b64,
                "reference_text": "",  # Leave empty for auto-transcription
            },
            timeout=120,  # 2 minute timeout
        )

        print(f"📥 Response status: {response.status_code}")

    except requests.exceptions.Timeout:
        print("❌ Request timed out after 2 minutes")
        exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        exit(1)

    # Parse response
    try:
        result = response.json()
        print("📋 Response received:")
        print(
            json.dumps(result, indent=2)[:500] + "..."
            if len(str(result)) > 500
            else json.dumps(result, indent=2)
        )

    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {response.text}")
        exit(1)

    # Check if request was successful
    if response.status_code == 200 and result.get("success", False):
        print("✅ Synthesis successful!")

        # Save result with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"generated_voice_{timestamp}.wav"

        try:
            result_audio = base64.b64decode(result["audio_data"])
            with open(output_filename, "wb") as f:
                f.write(result_audio)

            # Get file size for confirmation
            file_size = os.path.getsize(output_filename)
            print(f"🎵 Audio saved as '{output_filename}' ({file_size} bytes)")

        except Exception as e:
            print(f"❌ Error saving audio: {e}")

    else:
        print("❌ Synthesis failed!")
        if "error" in result:
            print(f"Error message: {result['error']}")
        elif "detail" in result:
            print(f"Error details: {result['detail']}")
        else:
            print(f"HTTP {response.status_code}: {response.text}")

    print("🏁 Test completed!")
