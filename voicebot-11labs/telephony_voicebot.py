"""
Telephony Voicebot - Twilio Integration
Handles phone calls with real-time voice processing
"""

import os
import asyncio
import base64
import json
from typing import Optional
from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from dotenv import load_dotenv
import openai
import numpy as np
from tts_11labs import ElevenLabsTTS
import audioop
import wave
from io import BytesIO
from rich.console import Console

# Load environment variables
load_dotenv()

# Initialize console
console = Console()

# Initialize FastAPI app
app = FastAPI(title="Telephony Voicebot")

# Global clients
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tts_client = ElevenLabsTTS()


class CallSession:
    """Manages a single phone call session"""
    
    def __init__(self, call_sid: str):
        self.call_sid = call_sid
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful phone assistant. Keep responses concise and natural for phone conversations. Be friendly and professional."}
        ]
        self.audio_buffer = BytesIO()
        self.transcript_buffer = ""
        self.is_speaking = False
        self.stream_sid = None
    
    async def process_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """Process incoming audio and return transcript if complete utterance detected"""
        # Convert from μ-law to PCM
        pcm_data = audioop.ulaw2lin(audio_data, 2)
        
        # Add to buffer
        self.audio_buffer.write(pcm_data)
        
        # Check if we have enough audio (simple VAD)
        if self.audio_buffer.tell() > 16000 * 2:  # 2 seconds of audio
            # Reset buffer position
            self.audio_buffer.seek(0)
            audio_bytes = self.audio_buffer.read()
            
            # Clear buffer
            self.audio_buffer = BytesIO()
            
            # Transcribe
            return await self.transcribe_audio(audio_bytes)
        
        return None
    
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Transcribe audio using Whisper API"""
        try:
            # Create WAV file in memory
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(8000)
                wav_file.writeframes(audio_bytes)
            
            wav_buffer.seek(0)
            wav_buffer.name = "audio.wav"
            
            # Transcribe using Whisper API
            transcript = await asyncio.to_thread(
                openai_client.audio.transcriptions.create,
                model="whisper-1",
                file=wav_buffer,
                language="en"
            )
            
            return transcript.text.strip()
            
        except Exception as e:
            console.print(f"[red]Transcription error: {str(e)}[/red]")
            return ""
    
    async def generate_response(self, user_input: str) -> str:
        """Generate AI response"""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=self.conversation_history,
            max_tokens=100,  # Keep responses short for phone
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Keep history manageable
        if len(self.conversation_history) > 10:
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-8:]
        
        return ai_response
    
    async def synthesize_speech(self, text: str) -> bytes:
        """Convert text to speech using 11Labs"""
        # Generate audio
        audio_bytes = await tts_client.async_generate_audio(text)
        
        # Convert to μ-law for telephony
        ulaw_audio = tts_client.convert_to_ulaw(audio_bytes)
        
        return ulaw_audio


# Store active sessions
active_sessions = {}


@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming phone call"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    from_number = form_data.get("From", "")
    
    console.print(f"[green]📞 Incoming call from {from_number}[/green]")
    
    # Create TwiML response
    response = VoiceResponse()
    response.say("Hello! I'm your AI assistant. How can I help you today?", voice="Polly.Amy")
    
    # Connect to WebSocket for streaming
    connect = Connect()
    stream = Stream(url=f"wss://{request.headers.get('host')}/voice/stream")
    stream.parameter(name="CallSid", value=call_sid)
    connect.append(stream)
    response.append(connect)
    
    return Response(content=str(response), media_type="text/xml")


@app.websocket("/voice/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connection for audio streaming"""
    await websocket.accept()
    
    call_sid = None
    session = None
    
    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            
            if data["event"] == "start":
                # Initialize session
                call_sid = data["start"]["callSid"]
                stream_sid = data["start"]["streamSid"]
                
                session = CallSession(call_sid)
                session.stream_sid = stream_sid
                active_sessions[call_sid] = session
                
                console.print(f"[blue]🔊 Stream started for call {call_sid}[/blue]")
            
            elif data["event"] == "media" and session:
                # Process audio chunk
                audio_payload = data["media"]["payload"]
                audio_chunk = base64.b64decode(audio_payload)
                
                # Process audio
                transcript = await session.process_audio_chunk(audio_chunk)
                
                if transcript and not session.is_speaking:
                    console.print(f"[green]User: {transcript}[/green]")
                    
                    # Generate response
                    session.is_speaking = True
                    response = await session.generate_response(transcript)
                    console.print(f"[blue]AI: {response}[/blue]")
                    
                    # Synthesize speech
                    audio_response = await session.synthesize_speech(response)
                    
                    # Send audio back
                    await send_audio_to_stream(websocket, audio_response, session.stream_sid)
                    
                    session.is_speaking = False
            
            elif data["event"] == "stop":
                # Clean up session
                if call_sid and call_sid in active_sessions:
                    del active_sessions[call_sid]
                console.print(f"[yellow]📴 Call ended: {call_sid}[/yellow]")
                break
                
    except Exception as e:
        console.print(f"[red]WebSocket error: {str(e)}[/red]")
    finally:
        if call_sid and call_sid in active_sessions:
            del active_sessions[call_sid]


async def send_audio_to_stream(websocket: WebSocket, audio_data: bytes, stream_sid: str):
    """Send audio data back to Twilio stream"""
    # Twilio expects base64 encoded μ-law audio in chunks
    chunk_size = 640  # 20ms of 8kHz μ-law audio
    
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        
        # Pad if necessary
        if len(chunk) < chunk_size:
            chunk += b'\x00' * (chunk_size - len(chunk))
        
        # Create media message
        media_message = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": base64.b64encode(chunk).decode("utf-8")
            }
        }
        
        await websocket.send_json(media_message)
        
        # Small delay to prevent overwhelming
        await asyncio.sleep(0.02)  # 20ms


@app.post("/voice/status")
async def handle_status_callback(request: Request):
    """Handle call status callbacks"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    call_status = form_data.get("CallStatus", "")
    
    console.print(f"[yellow]📊 Call {call_sid} status: {call_status}[/yellow]")
    
    return JSONResponse({"status": "ok"})


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Telephony Voicebot",
        "active_calls": len(active_sessions)
    }


def configure_twilio_webhook(ngrok_url: str):
    """Configure Twilio phone number with webhook URLs"""
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Find the phone number resource
    phone_numbers = twilio_client.incoming_phone_numbers.list(phone_number=phone_number)
    
    if phone_numbers:
        phone_number_sid = phone_numbers[0].sid
        
        # Update webhook URLs
        twilio_client.incoming_phone_numbers(phone_number_sid).update(
            voice_url=f"{ngrok_url}/voice/incoming",
            voice_method="POST",
            status_callback=f"{ngrok_url}/voice/status",
            status_callback_method="POST"
        )
        
        console.print(f"[green]✅ Configured Twilio webhooks for {phone_number}[/green]")
        console.print(f"[blue]Voice URL: {ngrok_url}/voice/incoming[/blue]")
    else:
        console.print(f"[red]❌ Phone number {phone_number} not found in Twilio account[/red]")


def main():
    """Main entry point"""
    console.print("[bold cyan]🤖 Telephony Voicebot with 11Labs[/bold cyan]")
    console.print("=" * 50)
    
    # Check environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        console.print(f"[red]❌ Missing environment variables: {', '.join(missing_vars)}[/red]")
        return
    
    # Instructions for ngrok
    console.print("\n[yellow]📡 Setup Instructions:[/yellow]")
    console.print("1. Install ngrok: https://ngrok.com/download")
    console.print("2. Start ngrok: ngrok http 8000")
    console.print("3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)")
    console.print("4. The app will configure Twilio webhooks automatically")
    console.print("\n[cyan]Or manually configure in Twilio Console:[/cyan]")
    console.print("   Voice URL: https://your-domain.com/voice/incoming")
    console.print("   Status Callback: https://your-domain.com/voice/status")
    
    # Get ngrok URL from user
    ngrok_url = input("\n🔗 Enter your ngrok HTTPS URL (or press Enter to skip): ").strip()
    
    if ngrok_url:
        configure_twilio_webhook(ngrok_url)
    
    # Start server
    console.print(f"\n[green]🚀 Starting server on http://localhost:8000[/green]")
    console.print(f"[blue]📞 Call {os.getenv('TWILIO_PHONE_NUMBER')} to test![/blue]")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main() 