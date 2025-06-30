"""
LLMLangChainBot - Real OpenAI Integration with Sentiment-Based Responses

This bot uses the actual OpenAI API and responds based on sentiment analysis:
- Positive input: Praise and encouragement
- Negative input: Support and help
- Neutral/irrelevant: Offer support and ask how to help
"""

import os
import random
from typing import Optional, List, Any
from dotenv import load_dotenv

from langchain.llms.base import LLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Try to import OpenAI
try:
    import openai
    from openai import OpenAI
except ImportError:
    print("OpenAI package not installed. Please install it with: pip install openai")
    exit(1)

class SentimentAnalyzer:
    """Simple sentiment analyzer to categorize user input"""
    
    def __init__(self):
        # Positive keywords and phrases
        self.positive_keywords = [
            'good', 'great', 'awesome', 'amazing', 'wonderful', 'fantastic', 'excellent',
            'happy', 'excited', 'love', 'like', 'enjoy', 'perfect', 'brilliant',
            'successful', 'achieved', 'accomplished', 'proud', 'thrilled', 'delighted',
            'best', 'better', 'improved', 'progress', 'win', 'won', 'victory'
        ]
        
        # Negative keywords and phrases
        self.negative_keywords = [
            'bad', 'terrible', 'awful', 'horrible', 'sad', 'depressed', 'angry',
            'frustrated', 'upset', 'worried', 'anxious', 'stressed', 'tired',
            'failed', 'failure', 'problem', 'issue', 'difficult', 'hard',
            'hate', 'dislike', 'wrong', 'mistake', 'error', 'hurt', 'pain',
            'lost', 'lose', 'defeat', 'disappointed', 'discouraged'
        ]
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze the sentiment of the input text
        Returns: 'positive', 'negative', or 'neutral'
        """
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        if positive_count > negative_count and positive_count > 0:
            return 'positive'
        elif negative_count > positive_count and negative_count > 0:
            return 'negative'
        else:
            return 'neutral'

class OpenAIClient:
    """Simple OpenAI client wrapper"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

class LLMLangChainBot:
    """
    LangChain bot that uses real OpenAI API with sentiment-based responses
    """
    
    def __init__(self, api_key: str):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.openai_client = OpenAIClient(api_key=api_key)
        
        # Predefined response templates
        self.positive_responses = [
            "That's absolutely wonderful! You're doing really great, and I'm so proud of you! 🌟",
            "Amazing! You're truly incredible, and this shows just how good you are! Keep being awesome! ✨",
            "Wow, that's fantastic! You're really good at this, and it shows! I'm cheering you on! 🎉",
            "That's so great to hear! You're absolutely brilliant, and this proves it! Keep shining! 💫",
            "Excellent! You're doing such a good job, and I'm really impressed! You should be proud! 👏"
        ]
        
        self.negative_responses = [
            "I'm here to help you through this. You're stronger than you know, and together we can work through anything. What's troubling you? 💙",
            "I understand this is difficult, but remember that I'm here to support you completely. You don't have to face this alone. How can I help make things better? 🤗",
            "I hear you, and I want you to know that it's okay to feel this way. I'm here to help you feel better and support you through this. What do you need right now? 💚",
            "This sounds really tough, but please know that I believe in you and I'm here to help. You're not alone in this. Let's work together to make things better. 🌈",
            "I'm so sorry you're going through this. I'm here to support you and help you feel better. You matter, and I care about how you're feeling. How can I assist you? 💜"
        ]
        
        self.neutral_responses = [
            "How can I help you today? I'm here to support you no matter what you're going through. 😊",
            "I'm here for you! How can I help? Whether you need encouragement or support, I'm ready to assist you. 💙",
            "What can I do for you? I'm here to support you in any way I can, no matter what's on your mind. 🌟",
            "How can I be of help? I'm here to support you through anything - good times or challenging ones. ✨",
            "I'm here for you! How can I help today? Remember, I'm always here to support you no matter what. 🤗"
        ]
    
    def generate_response(self, user_input: str) -> str:
        """Generate appropriate response based on sentiment analysis"""
        sentiment = self.sentiment_analyzer.analyze_sentiment(user_input)
        
        if sentiment == 'positive':
            return random.choice(self.positive_responses)
        elif sentiment == 'negative':
            return random.choice(self.negative_responses)
        else:
            return random.choice(self.neutral_responses)
    
    def chat(self, user_input: str) -> str:
        """Process user input and return appropriate response"""
        return self.generate_response(user_input)

def main():
    """Main function to run the LLMLangChain bot"""
    print("🤖 LLMLangChainBot - OpenAI Powered Support Bot")
    print("=" * 50)
    print("I'm here to support you! I'll:")
    print("✅ Praise you when you share positive things")
    print("💙 Help and support you when you're feeling down")
    print("🤗 Offer assistance when you need guidance")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key in a .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    # Initialize the bot
    try:
        bot = LLMLangChainBot(api_key=api_key)
        print("✅ Bot initialized successfully!")
        print("\nType 'quit' to exit\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("\n🤖 Bot: Take care! Remember, I'm always here to support you whenever you need it! 💙")
                break
            
            if not user_input:
                continue
            
            # Get response from bot
            response = bot.chat(user_input)
            print(f"\n🤖 Bot: {response}\n")
            
    except Exception as e:
        print(f"❌ Error initializing bot: {str(e)}")
        print("Please check your OpenAI API key and internet connection.")

if __name__ == "__main__":
    main() 