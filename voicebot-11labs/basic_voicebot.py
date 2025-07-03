"""
Basic Voicebot - Local microphone and speaker
Complete voice assistant using 11Labs TTS and OpenAI Whisper STT
"""

import os
import sys
import time
import queue
import threading
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv
import openai
import whisper
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from tts_11labs import ElevenLabsTTS
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize console for beautiful output
console = Console()

class BasicVoicebot:
    """Basic voice assistant with mic input and speaker output"""
    
    def __init__(self):
        """Initialize all components"""
        console.print("[bold green]🤖 Initializing Voicebot...[/bold green]")
        
        # Initialize APIs
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tts = ElevenLabsTTS()
        
        # Load Whisper model
        console.print("📥 Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 0.5  # seconds
        self.silence_threshold = 0.01
        self.silence_duration = 2.0  # seconds of silence to stop recording
        
        # Recording state
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recorded_audio = []
        
        # Conversation history
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful, friendly voice assistant. Keep responses concise and natural for speech."}
        ]
        
        console.print("[bold green]✅ Voicebot initialized![/bold green]")
    
    def record_audio(self):
        """Record audio from microphone until silence detected"""
        self.recorded_audio = []
        self.is_recording = True
        silence_counter = 0
        
        def audio_callback(indata, frames, time, status):
            if status:
                console.print(f"[red]Audio error: {status}[/red]")
            
            # Calculate volume
            volume = np.sqrt(np.mean(indata**2))
            
            # Check for silence
            if volume < self.silence_threshold:
                silence_counter += self.chunk_duration
            else:
                silence_counter = 0
            
            # Stop recording after silence duration
            if silence_counter >= self.silence_duration:
                self.is_recording = False
            
            # Add to recording buffer
            if self.is_recording:
                self.audio_queue.put(indata.copy())
        
        # Start recording
        console.print("\n[cyan]🎤 Listening... (speak now)[/cyan]")
        
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=audio_callback,
            blocksize=int(self.sample_rate * self.chunk_duration)
        ):
            while self.is_recording:
                time.sleep(0.1)
        
        # Collect recorded audio
        while not self.audio_queue.empty():
            self.recorded_audio.append(self.audio_queue.get())
        
        if self.recorded_audio:
            audio_data = np.concatenate(self.recorded_audio, axis=0)
            return audio_data.flatten()
        return None
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper"""
        console.print("[yellow]📝 Transcribing...[/yellow]")
        
        # Whisper expects float32 audio
        audio_float = audio_data.astype(np.float32)
        
        # Transcribe
        result = self.whisper_model.transcribe(
            audio_float,
            language="en",
            fp16=False
        )
        
        text = result["text"].strip()
        console.print(f"[green]You said:[/green] {text}")
        return text
    
    def generate_response(self, user_input):
        """Generate AI response using OpenAI"""
        console.print("[yellow]🤔 Thinking...[/yellow]")
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Generate response
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.conversation_history,
            max_tokens=150,  # Keep responses concise for speech
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Add to history
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Keep history manageable
        if len(self.conversation_history) > 10:
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-8:]
        
        return ai_response
    
    def speak_response(self, text):
        """Convert text to speech and play it"""
        console.print(f"[blue]AI:[/blue] {text}")
        console.print("[yellow]🔊 Speaking...[/yellow]")
        
        # Generate audio
        audio_bytes = self.tts.generate_audio(text)
        
        # Play audio
        audio = AudioSegment.from_mp3(BytesIO(audio_bytes))
        play(audio)
    
    def run(self):
        """Main conversation loop"""
        console.print(Panel.fit(
            "[bold cyan]Voice Assistant Ready![/bold cyan]\n\n"
            "🎤 Press ENTER to speak\n"
            "🛑 Type 'quit' to exit\n"
            "📝 Type text to send without speaking",
            title="🤖 11Labs Voicebot"
        ))
        
        while True:
            try:
                # Wait for user input
                user_action = input("\n> ").strip().lower()
                
                if user_action == 'quit':
                    console.print("[red]👋 Goodbye![/red]")
                    break
                
                elif user_action == '':
                    # Record audio
                    audio_data = self.record_audio()
                    
                    if audio_data is not None and len(audio_data) > 0:
                        # Transcribe
                        user_input = self.transcribe_audio(audio_data)
                        
                        if user_input:
                            # Generate response
                            response = self.generate_response(user_input)
                            
                            # Speak response
                            self.speak_response(response)
                    else:
                        console.print("[yellow]No audio detected. Try again.[/yellow]")
                
                else:
                    # Text input
                    console.print(f"[green]You typed:[/green] {user_action}")
                    
                    # Generate response
                    response = self.generate_response(user_action)
                    
                    # Speak response
                    self.speak_response(response)
                    
            except KeyboardInterrupt:
                console.print("\n[red]Interrupted. Goodbye![/red]")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                console.print("[yellow]Please try again.[/yellow]")


def check_microphone():
    """Check if microphone is available"""
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if not input_devices:
            console.print("[red]❌ No microphone found![/red]")
            console.print("Please connect a microphone and try again.")
            return False
        
        console.print(f"[green]✅ Found {len(input_devices)} microphone(s)[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error checking microphone: {str(e)}[/red]")
        return False


def main():
    """Main entry point"""
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ OPENAI_API_KEY not found in .env file[/red]")
        sys.exit(1)
    
    if not os.getenv("ELEVENLABS_API_KEY"):
        console.print("[red]❌ ELEVENLABS_API_KEY not found in .env file[/red]")
        sys.exit(1)
    
    # Check microphone
    if not check_microphone():
        sys.exit(1)
    
    # Run voicebot
    try:
        bot = BasicVoicebot()
        bot.run()
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 