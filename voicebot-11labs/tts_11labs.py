"""
11Labs Text-to-Speech Wrapper
Handles voice synthesis with streaming support
"""

import os
import asyncio
from typing import Optional, AsyncGenerator, Union
from elevenlabs import Voice, VoiceSettings, generate, stream, set_api_key
from elevenlabs.client import ElevenLabs
import numpy as np
from io import BytesIO

class ElevenLabsTTS:
    """Wrapper for 11Labs Text-to-Speech API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize 11Labs TTS client"""
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        
        # Initialize client
        self.client = ElevenLabs(api_key=self.api_key)
        set_api_key(self.api_key)
        
        # Default voice settings
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        self.default_model = "eleven_monolingual_v1"
        
        # Voice settings for natural conversation
        self.voice_settings = VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=True
        )
    
    def list_voices(self):
        """List all available voices"""
        voices = self.client.voices.get_all()
        return [(voice.voice_id, voice.name) for voice in voices.voices]
    
    def generate_audio(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Generate audio from text (non-streaming)
        Returns audio bytes in MP3 format
        """
        voice_id = voice_id or self.default_voice_id
        
        audio = generate(
            text=text,
            voice=voice_id,
            model=self.default_model
        )
        
        # Convert generator to bytes
        audio_bytes = b''.join(audio)
        return audio_bytes
    
    def stream_audio(self, text: str, voice_id: Optional[str] = None):
        """
        Stream audio generation for lower latency
        Yields audio chunks as they're generated
        """
        voice_id = voice_id or self.default_voice_id
        
        audio_stream = stream(
            text=text,
            voice=voice_id,
            model=self.default_model,
            stream_chunk_size=1024
        )
        
        for chunk in audio_stream:
            yield chunk
    
    async def async_generate_audio(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Async version of generate_audio"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_audio, text, voice_id)
    
    async def async_stream_audio(self, text: str, voice_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
        """Async streaming audio generation"""
        voice_id = voice_id or self.default_voice_id
        
        # Run synchronous stream in executor
        loop = asyncio.get_event_loop()
        
        def _stream():
            return list(self.stream_audio(text, voice_id))
        
        chunks = await loop.run_in_executor(None, _stream)
        
        for chunk in chunks:
            yield chunk
    
    def convert_to_pcm(self, audio_bytes: bytes, sample_rate: int = 16000) -> np.ndarray:
        """Convert MP3 audio bytes to PCM numpy array"""
        from pydub import AudioSegment
        
        # Load MP3 from bytes
        audio = AudioSegment.from_mp3(BytesIO(audio_bytes))
        
        # Convert to target sample rate
        audio = audio.set_frame_rate(sample_rate)
        
        # Convert to mono
        audio = audio.set_channels(1)
        
        # Get raw audio data
        samples = np.array(audio.get_array_of_samples())
        
        # Normalize to [-1, 1]
        samples = samples.astype(np.float32) / 32768.0
        
        return samples
    
    def convert_to_ulaw(self, audio_bytes: bytes) -> bytes:
        """Convert MP3 audio to μ-law format for telephony"""
        from pydub import AudioSegment
        
        # Load MP3 from bytes
        audio = AudioSegment.from_mp3(BytesIO(audio_bytes))
        
        # Convert to 8kHz mono (telephony standard)
        audio = audio.set_frame_rate(8000)
        audio = audio.set_channels(1)
        
        # Export as μ-law
        output = BytesIO()
        audio.export(output, format="mulaw")
        return output.getvalue()


class VoiceManager:
    """Manage voice profiles and settings"""
    
    def __init__(self, tts_client: ElevenLabsTTS):
        self.tts = tts_client
        
        # Predefined voice profiles
        self.voice_profiles = {
            "assistant": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
                "name": "Rachel",
                "description": "Professional and friendly assistant"
            },
            "support": {
                "voice_id": "AZnzlk1XvdvUeBnXmlld",  # Domi
                "name": "Domi",
                "description": "Warm and empathetic support agent"
            },
            "narrator": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella
                "name": "Bella",
                "description": "Clear and engaging narrator"
            }
        }
    
    def get_voice_for_context(self, context: str) -> str:
        """Select appropriate voice based on conversation context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["help", "support", "problem", "issue"]):
            return self.voice_profiles["support"]["voice_id"]
        elif any(word in context_lower for word in ["story", "explain", "describe"]):
            return self.voice_profiles["narrator"]["voice_id"]
        else:
            return self.voice_profiles["assistant"]["voice_id"]


# Example usage
if __name__ == "__main__":
    # Initialize TTS
    tts = ElevenLabsTTS()
    
    # List available voices
    print("Available voices:")
    for voice_id, name in tts.list_voices():
        print(f"  {name}: {voice_id}")
    
    # Generate sample audio
    text = "Hello! I'm your AI assistant powered by 11Labs. How can I help you today?"
    
    print("\nGenerating audio...")
    audio_bytes = tts.generate_audio(text)
    
    # Save to file
    with open("sample_output.mp3", "wb") as f:
        f.write(audio_bytes)
    
    print("Audio saved to sample_output.mp3")
    
    # Test streaming
    print("\nTesting streaming...")
    for i, chunk in enumerate(tts.stream_audio("This is a streaming test.")):
        print(f"Received chunk {i+1}: {len(chunk)} bytes") 