# 11Labs Voicebot - Complete Guide

## Overview
This project implements a voice-based conversational AI bot using:
- **11Labs** for Text-to-Speech (TTS)
- **OpenAI Whisper** for Speech-to-Text (STT)
- **OpenAI GPT** for conversational AI
- **Twilio** for telephony integration
- **WebSockets** for real-time communication

## Architecture

### Core Components:
1. **Telephony Layer** (Twilio/Vonage/Plivo)
   - Handles incoming/outgoing calls
   - Manages SIP connections
   - Streams audio via WebSocket

2. **Speech Processing**
   - STT: Converts user speech to text
   - TTS: Converts bot responses to speech (11Labs)

3. **AI Brain**
   - Processes user input
   - Generates appropriate responses
   - Maintains conversation context

4. **Audio Pipeline**
   - Real-time audio streaming
   - Format conversion (μ-law/PCM)
   - Buffering and optimization

## Prerequisites

- Python 3.8+
- Twilio account (for telephony)
- 11Labs API key
- OpenAI API key
- ngrok (for local development)

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file:
```
ELEVENLABS_API_KEY=your_11labs_key
OPENAI_API_KEY=your_openai_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Quick Start

1. **Basic Voice Assistant (Local)**
   ```bash
   python basic_voicebot.py
   ```

2. **Telephony Integration**
   ```bash
   python telephony_voicebot.py
   ```

3. **WebSocket Server**
   ```bash
   python websocket_server.py
   ```

## Project Structure

```
voicebot-11labs/
├── basic_voicebot.py      # Simple voice assistant
├── telephony_voicebot.py  # Twilio integration
├── websocket_server.py    # Real-time audio streaming
├── audio_processor.py     # Audio format handling
├── conversation_manager.py # AI conversation logic
├── tts_11labs.py         # 11Labs TTS wrapper
├── stt_whisper.py        # Whisper STT wrapper
├── requirements.txt       # Dependencies
└── .env                  # Environment variables
```

## Key Features

- **Real-time conversation** with minimal latency
- **Natural voice synthesis** using 11Labs
- **Accurate speech recognition** with Whisper
- **Telephone integration** via Twilio
- **WebSocket support** for streaming audio
- **Conversation memory** and context awareness
- **Interrupt handling** for natural conversations

## Testing

1. **Local Testing**: Use `basic_voicebot.py` with microphone
2. **Phone Testing**: Configure Twilio webhook to your ngrok URL
3. **Load Testing**: Use `test_concurrent_calls.py`

## Deployment

See `deployment/` folder for:
- Docker configuration
- AWS/GCP deployment guides
- Kubernetes manifests
- Load balancing setup 