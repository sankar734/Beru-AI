import struct
import math
from typing import Optional
from pydantic import BaseModel

class TranscriptionResult(BaseModel):
    transcript: str
    duration_seconds: float
    confidence: float

class SynthesisResult(BaseModel):
    audio_bytes: bytes
    format: str = "audio/wav"
    sample_rate: int = 16000
    duration_seconds: float

class VoiceEngine:
    """Voice Engine providing Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities."""

    async def transcribe(self, audio_bytes: bytes, filename: Optional[str] = "audio.wav") -> TranscriptionResult:
        # In mock/offline mode, produce clean transcript
        duration = round(len(audio_bytes) / 32000.0, 2) if audio_bytes else 1.5
        transcript = "Hey NOVA, open VS Code and run my frontend development server."
        return TranscriptionResult(
            transcript=transcript,
            duration_seconds=max(0.5, duration),
            confidence=0.97
        )

    async def synthesize(self, text: str, voice: str = "nova-voice-default") -> SynthesisResult:
        # Generate a minimal valid 16kHz mono PCM WAV header + 0.5s tone
        sample_rate = 16000
        num_samples = int(sample_rate * 0.5)
        # 44-byte WAV header
        header = bytearray(44)
        header[0:4] = b"RIFF"
        struct.pack_into("<I", header, 4, 36 + num_samples * 2)
        header[8:12] = b"WAVE"
        header[12:16] = b"fmt "
        struct.pack_into("<IHHIIHH", header, 16, 16, 1, 1, sample_rate, sample_rate * 2, 2, 16)
        header[36:40] = b"data"
        struct.pack_into("<I", header, 40, num_samples * 2)

        # Generate smooth 440Hz tone
        pcm_data = bytearray(num_samples * 2)
        for i in range(num_samples):
            sample = int(math.sin(2 * math.pi * 440 * (i / sample_rate)) * 10000)
            struct.pack_into("<h", pcm_data, i * 2, sample)

        full_wav = bytes(header + pcm_data)
        return SynthesisResult(
            audio_bytes=full_wav,
            format="audio/wav",
            sample_rate=sample_rate,
            duration_seconds=0.5
        )

voice_engine = VoiceEngine()
