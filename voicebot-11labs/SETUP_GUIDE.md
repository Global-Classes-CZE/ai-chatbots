# Complete Setup Guide for 11Labs Voicebot

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Account Setup](#account-setup)
3. [Environment Configuration](#environment-configuration)
4. [Local Development](#local-development)
5. [Telephony Integration](#telephony-integration)
6. [Advanced Features](#advanced-features)
7. [Deployment Options](#deployment-options)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Python 3.8 or higher
- pip (Python package manager)
- Git
- ngrok (for local telephony testing)
- FFmpeg (for audio processing)

### Installing FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Account Setup

### 1. 11Labs Account
1. Sign up at [11Labs](https://elevenlabs.io/)
2. Navigate to Profile → API Keys
3. Copy your API key
4. Note: Free tier includes 10,000 characters/month

### 2. OpenAI Account
1. Sign up at [OpenAI](https://platform.openai.com/)
2. Go to API Keys section
3. Create new secret key
4. Save the key securely

### 3. Twilio Account (for telephony)
1. Sign up at [Twilio](https://www.twilio.com/)
2. Verify your phone number
3. Get a Twilio phone number:
   - Console → Phone Numbers → Manage → Buy a number
   - Choose a number with Voice capabilities
4. Note your credentials:
   - Account SID (from Console Dashboard)
   - Auth Token (from Console Dashboard)
   - Phone Number (format: +1234567890)

## Environment Configuration

### 1. Clone and Setup
```bash
# Clone the repository (or create new directory)
mkdir voicebot-11labs
cd voicebot-11labs

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Create .env file
```bash
# Create .env file in project root
touch .env
```

Add the following to `.env`:
```env
# API Keys
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Twilio Configuration (for telephony)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Optional: Custom settings
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
WHISPER_MODEL=base
```

## Local Development

### Testing Basic Voicebot
```bash
# Run the basic voicebot with microphone
python basic_voicebot.py
```

Features:
- Press ENTER to start speaking
- Type text to skip voice input
- Type 'quit' to exit

### Common Issues:
1. **Microphone not found**: Check system permissions
2. **Audio playback issues**: Install pyaudio dependencies
3. **Slow response**: First run downloads Whisper model

## Telephony Integration

### 1. Install ngrok
```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

### 2. Start ngrok tunnel
```bash
# In a separate terminal
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 3. Run telephony server
```bash
python telephony_voicebot.py
```

When prompted, paste your ngrok URL. The script will:
- Configure Twilio webhooks automatically
- Start the FastAPI server
- Display the phone number to call

### 4. Test the system
- Call your Twilio phone number
- Speak naturally after the greeting
- The bot will respond with 11Labs voice

## Advanced Features

### 1. Custom Voices
Browse and test voices at [11Labs Voice Library](https://elevenlabs.io/voice-library)

Update voice in code:
```python
tts.default_voice_id = "your_preferred_voice_id"
```

### 2. Voice Cloning (Pro feature)
```python
# Upload voice samples to 11Labs
# Use the cloned voice ID in your app
```

### 3. Conversation Context
Modify system prompts for different use cases:
```python
# Customer support bot
system_prompt = "You are a helpful customer support agent..."

# Sales assistant
system_prompt = "You are a friendly sales assistant..."

# Medical receptionist
system_prompt = "You are a medical receptionist..."
```

### 4. Real-time Interruption Handling
The telephony version supports:
- Voice Activity Detection (VAD)
- Interrupt detection
- Barge-in capability

## Deployment Options

### 1. Local Server + Tunneling
- Good for: Testing, demos
- Tools: ngrok, localtunnel, cloudflare tunnel

### 2. Cloud Deployment

#### AWS EC2
```bash
# Install on Ubuntu instance
sudo apt update
sudo apt install python3-pip python3-venv
# Follow setup steps above
```

#### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "telephony_voicebot.py"]
```

#### Serverless (AWS Lambda + API Gateway)
- Use Zappa or Serverless Framework
- Note: WebSocket support requires API Gateway v2

### 3. Production Considerations
- Use environment variables for secrets
- Implement rate limiting
- Add logging and monitoring
- Set up SSL certificates
- Configure auto-scaling

## Troubleshooting

### Common Issues

1. **"No module named 'elevenlabs'"**
   ```bash
   pip install elevenlabs
   ```

2. **Twilio webhook not receiving calls**
   - Verify ngrok is running
   - Check Twilio phone number configuration
   - Ensure firewall allows incoming connections

3. **Audio quality issues**
   - Check internet bandwidth
   - Adjust audio encoding settings
   - Use closer Twilio/11Labs regions

4. **High latency**
   - Use streaming TTS
   - Optimize prompt length
   - Consider edge deployment

### Debug Mode
Add to your code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

1. **Reduce latency**:
   - Use 11Labs streaming API
   - Implement audio pre-buffering
   - Use WebSocket for real-time communication

2. **Scale for multiple calls**:
   - Use async/await properly
   - Implement connection pooling
   - Consider load balancing

## Cost Optimization

### 11Labs
- Free: 10,000 characters/month
- Starter: $5/month for 30,000 characters
- Creator: $22/month for 100,000 characters

### OpenAI
- Whisper API: $0.006/minute
- GPT-3.5: $0.0005/1K input tokens

### Twilio
- Phone number: $1-2/month
- Incoming calls: $0.0085/minute
- Outgoing calls: varies by destination

## Next Steps

1. **Enhance the bot**:
   - Add database for conversation history
   - Implement user authentication
   - Add analytics and monitoring

2. **Integrate with services**:
   - CRM systems (Salesforce, HubSpot)
   - Calendar booking
   - Payment processing

3. **Advanced features**:
   - Multi-language support
   - Sentiment analysis
   - Call recording and transcription

## Resources

- [11Labs Documentation](https://docs.elevenlabs.io/)
- [Twilio Voice Docs](https://www.twilio.com/docs/voice)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error logs
3. Test with simplified examples
4. Check API service status pages 