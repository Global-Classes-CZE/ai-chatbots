#!/bin/bash

# Installation script for Lesson 1: LangChain Chatbot
# This script sets up the environment and installs all required dependencies

echo "🚀 Setting up Lesson 1: LangChain Chatbot"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ All dependencies installed successfully!"
else
    echo "❌ requirements.txt not found. Installing minimal dependencies..."
    pip install langchain>=0.1.0 langchain-core>=0.1.0 typing-extensions>=4.5.0
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To run the chatbots:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run simple bot: python simple_langchain_bot.py"
echo "3. Run advanced bot: python langchain_chatbot.py"
echo ""
echo "To deactivate the virtual environment later: deactivate" 