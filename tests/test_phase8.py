import io
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.database import db_manager
from services.ai_core.multimodal.vision_engine import vision_engine
from services.ai_core.multimodal.voice_engine import voice_engine

@pytest.mark.asyncio
async def test_vision_engine_and_secret_redaction():
    # Test secret redactor
    raw_snippet = "token = 'sk-abcdef1234567890abcdef1234567890' in system logs"
    redacted, was_redacted = vision_engine.redact_secrets(raw_snippet)
    assert was_redacted is True
    assert "[REDACTED_SECRET]" in redacted
    assert "sk-" not in redacted

    # Test analyze error screenshot
    result = await vision_engine.analyze(
        image_bytes=b"fake-png-data",
        prompt="Explain this python error screenshot",
        filename="error_trace.png"
    )
    assert result.confidence > 0.90
    assert result.redacted_sensitive_data is True
    assert "ValueError" in result.analysis

@pytest.mark.asyncio
async def test_voice_engine_stt_tts():
    # Test STT
    trans_res = await voice_engine.transcribe(audio_bytes=b"fake-audio-bytes")
    assert "NOVA" in trans_res.transcript
    assert trans_res.confidence > 0.90

    # Test TTS
    synth_res = await voice_engine.synthesize("System ready for instructions.")
    assert synth_res.format == "audio/wav"
    assert len(synth_res.audio_bytes) > 44  # Has valid WAV header + audio samples
    assert synth_res.audio_bytes[0:4] == b"RIFF"

@pytest.mark.asyncio
async def test_media_endpoints():
    await db_manager.connect()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Auth token
        auth_res = await client.post("/api/v1/auth/register", json={
            "email": "mediauser@novax.local",
            "name": "Media Specialist",
            "password": "MediaPassword123!"
        })
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Vision analyze endpoint
        files = {"file": ("screenshot.png", io.BytesIO(b"png-data"), "image/png")}
        data = {"prompt": "What is the error in this screenshot?"}
        vis_res = await client.post("/api/v1/media/vision/analyze", files=files, data=data, headers=headers)
        assert vis_res.status_code == 200
        assert "analysis" in vis_res.json()

        # 2. Voice transcribe endpoint
        audio_files = {"file": ("voice.wav", io.BytesIO(b"audio-data"), "audio/wav")}
        voice_res = await client.post("/api/v1/media/voice/transcribe", files=audio_files, headers=headers)
        assert voice_res.status_code == 200
        assert "transcript" in voice_res.json()

        # 3. Voice synthesize endpoint
        synth_res = await client.post("/api/v1/media/voice/synthesize", json={
            "text": "Task completed successfully."
        }, headers=headers)
        assert synth_res.status_code == 200
        assert synth_res.headers["content-type"] == "audio/wav"
        assert synth_res.content[:4] == b"RIFF"

        # 4. Image generate endpoint
        img_res = await client.post("/api/v1/media/image/generate", json={
            "prompt": "Futuristic AI operating system dashboard with sleek glassmorphism"
        }, headers=headers)
        assert img_res.status_code == 200
        assert img_res.json()["status"] == "success"
