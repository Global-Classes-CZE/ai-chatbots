@echo off
REM Installation script for Lesson 1: LangChain Chatbot (Windows)
REM This script sets up the environment and installs all required dependencies

echo 🚀 Setting up Lesson 1: LangChain Chatbot
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Show Python version
for /f "tokens=2" %%i in ('python --version') do echo ✅ Found Python %%i

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📥 Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ All dependencies installed successfully!
) else (
    echo ❌ requirements.txt not found. Installing minimal dependencies...
    pip install "langchain>=0.1.0" "langchain-core>=0.1.0" "typing-extensions>=4.5.0"
)

echo.
echo 🎉 Installation complete!
echo.
echo To run the chatbots:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run simple bot: python simple_langchain_bot.py
echo 3. Run advanced bot: python langchain_chatbot.py
echo.
echo To deactivate the virtual environment later: deactivate
echo.
pause 