import modal
import os
import tempfile
import base64
import json

# Create Modal app
app = modal.App("f5-tts-voxify")

# Define the container image with F5-TTS
image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg")
    .pip_install([
        "torch==2.0.1",
        "torchaudio==2.0.2",
        "transformers",
        "accelerate",
        "librosa",
        "soundfile",
        "numpy",
        "scipy",
        "einops",
        "tensorboard",
        "matplotlib",
        "jieba",
        "fastapi",
        "pydantic",
        "cached-path"
    ])
    .run_commands([
        "git clone https://github.com/SWivid/F5-TTS.git /app/F5-TTS",
        "cd /app/F5-TTS && pip install -e ."
    ])
    .env({"PYTHONPATH": "/app/F5-TTS"})
)


@app.function(
    image=image,
    gpu="T4",
    timeout=600,
    container_idle_timeout=120
)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import sys
    sys.path.insert(0, '/app/F5-TTS')

    app = FastAPI()

    class SynthesisRequest(BaseModel):
        text: str
        reference_audio_b64: str

    @app.post("/synthesize")
    async def synthesize_speech(request: SynthesisRequest):
        try:
            print(f"Received synthesis request for text: {request.text[:50]}...")

            # Import F5-TTS modules
            import sys
            sys.path.insert(0, '/app/F5-TTS')

            # More specific imports
            from f5_tts.model import DiT
            from f5_tts.infer.utils_infer import load_model, load_vocoder
            import torchaudio
            import torch

            text = request.text
            reference_audio_b64 = request.reference_audio_b64

            if not text or not reference_audio_b64:
                return {
                    "success": False,
                    "error": "Missing text or reference_audio_b64"
                }

            print("Loading F5-TTS models...")

            # Try more explicit model loading
            try:
                # Load model with explicit parameters
                model, vocab_char_map, vocab_size = load_model(
                    model_type="F5-TTS",
                    model_name="F5-TTS",
                    device="cuda"
                )
                vocoder = load_vocoder(vocoder_name="vocos")
                print("Models loaded successfully!")
            except Exception as model_error:
                print(f"Model loading error: {model_error}")
                return {
                    "success": False,
                    "error": f"Model loading failed: {str(model_error)}"
                }

            print("Decoding reference audio...")
            # Decode reference audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as ref_file:
                audio_data = base64.b64decode(reference_audio_b64)
                ref_file.write(audio_data)
                ref_path = ref_file.name

            print("Starting speech synthesis...")

            # Try manual inference instead of infer_process
            try:
                from f5_tts.infer.utils_infer import infer_process

                # Call with explicit arguments
                generated_audio = infer_process(
                    ref_file=ref_path,
                    gen_text=text,
                    model=model,
                    vocoder=vocoder,
                    vocab_char_map=vocab_char_map,
                    vocab_size=vocab_size,
                    speed=1.0,
                    show_info=print,
                    progress=print,
                    target_sample_rate=24000,
                    n_mel_channels=100,
                    hop_length=256,
                    win_length=1024,
                    n_fft=1024,
                    mel_spec_type="vocos"
                )

            except Exception as synth_error:
                print(f"Synthesis error: {synth_error}")
                # Try simpler approach
                try:
                    generated_audio = infer_process(
                        ref_path,
                        text,
                        model,
                        vocoder,
                        vocab_char_map,
                        vocab_size
                    )
                except Exception as simple_error:
                    return {
                        "success": False,
                        "error": f"Both synthesis methods failed: {str(simple_error)}"
                    }

            print("Saving generated audio...")
            # Generate speech
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                # Save and read result
                torchaudio.save(output_file.name, generated_audio, 24000)

                with open(output_file.name, 'rb') as f:
                    result_audio = f.read()

            # Cleanup
            os.unlink(ref_path)
            os.unlink(output_file.name)

            print("Synthesis completed successfully!")
            return {
                "success": True,
                "audio_data": base64.b64encode(result_audio).decode(),
                "message": "Speech synthesized successfully"
            }

        except Exception as e:
            print(f"Error during synthesis: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Synthesis failed: {str(e)}"
            }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "model": "F5-TTS", "python_version": "3.10"}

    @app.get("/debug")
    async def debug_info():
        """Debug endpoint to check F5-TTS installation"""
        try:
            import sys
            sys.path.insert(0, '/app/F5-TTS')

            from f5_tts.infer.utils_infer import load_model
            import torch

            return {
                "cuda_available": torch.cuda.is_available(),
                "cuda_device_count": torch.cuda.device_count(),
                "f5_tts_path": "/app/F5-TTS",
                "python_path": sys.path[:3]
            }
        except Exception as e:
            return {"error": str(e)}

    return app