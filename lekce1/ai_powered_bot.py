"""
AI Powered Bot - Full LLM Integration

This bot uses the OpenAI LLM for everything:
- Sentiment analysis through LLM
- Response generation through LLM
- No predefined responses or keyword matching
- Pure AI-driven conversation
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Try to import OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI package not installed. Please install it with: pip install openai")
    exit(1)

class AIPoweredBot:
    """
    A bot that uses LLM for both sentiment analysis and response generation
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # System prompts for different tasks
        self.sentiment_analysis_prompt = """
        You are a sentiment analyzer. Analyze the emotional tone of the user's message and respond with ONLY ONE of these three words:
        - POSITIVE (if the message expresses happiness, success, achievement, or good feelings)
        - NEGATIVE (if the message expresses sadness, problems, failures, or bad feelings)  
        - NEUTRAL (if the message is neither clearly positive nor negative, or is just informational)
        
        Respond with only the single word classification, nothing else.
        
        User message: "{user_input}"
        """
        
        self.response_generation_prompts = {
            'positive': """
            The user has shared something positive with you. Generate a warm, encouraging response that:
            - Celebrates their success or good feelings
            - Tells them they're doing great and you're proud of them
            - Shows genuine excitement for them
            - Keeps the response conversational and supportive
            - Use encouraging language and maybe an emoji
            
            User's positive message: "{user_input}"
            """,
            
            'negative': """
            The user has shared something negative or is going through a difficult time. Generate a compassionate, supportive response that:
            - Acknowledges their feelings with empathy
            - Offers genuine support and help
            - Lets them know they're not alone
            - Asks how you can help or what they need
            - Shows that you care and are there for them
            - Use comforting language and maybe a supportive emoji
            
            User's message about their difficulty: "{user_input}"
            """,
            
            'neutral': """
            The user has shared something neutral or unclear. Generate a helpful response that:
            - Offers assistance and support
            - Asks how you can help them
            - Emphasizes that you're there to support them no matter what
            - Shows you're ready to help with whatever they need
            - Keeps the tone warm and welcoming
            - Use supportive language and maybe a friendly emoji
            
            User's neutral message: "{user_input}"
            """
        }
    
    def analyze_sentiment_with_llm(self, user_input: str) -> str:
        """
        Use LLM to analyze the sentiment of user input
        Returns: 'positive', 'negative', or 'neutral'
        """
        try:
            prompt = self.sentiment_analysis_prompt.format(user_input=user_input)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,  # We only need one word
                temperature=0.1  # Low temperature for consistent classification
            )
            
            sentiment = response.choices[0].message.content.strip().upper()
            
            # Map to our expected values
            if sentiment == "POSITIVE":
                return "positive"
            elif sentiment == "NEGATIVE":
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return "neutral"  # Default to neutral on error
    
    def generate_response_with_llm(self, user_input: str, sentiment: str) -> str:
        """
        Use LLM to generate appropriate response based on sentiment
        """
        try:
            prompt = self.response_generation_prompts[sentiment].format(user_input=user_input)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8  # Higher temperature for more creative responses
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I'm sorry, I encountered an error while generating a response: {str(e)}"
    
    def chat(self, user_input: str) -> tuple[str, str]:
        """
        Process user input and return both sentiment and response
        Returns: (sentiment, response)
        """
        # Step 1: Analyze sentiment using LLM
        sentiment = self.analyze_sentiment_with_llm(user_input)
        
        # Step 2: Generate response using LLM based on sentiment
        response = self.generate_response_with_llm(user_input, sentiment)
        
        return sentiment, response
    
    def chat_simple(self, user_input: str) -> str:
        """
        Simple chat method that returns just the response
        """
        _, response = self.chat(user_input)
        return response

def main():
    """Main function to run the AI Powered Bot"""
    print("🤖 AI Powered Bot - Full LLM Integration")
    print("=" * 50)
    print("This bot uses AI for everything:")
    print("🧠 LLM analyzes your sentiment")
    print("💬 LLM generates personalized responses")
    print("✨ No predefined responses - pure AI!")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key in a .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("See env_setup_instructions.txt for detailed setup steps.")
        return
    
    # Initialize the bot
    try:
        bot = AIPoweredBot(api_key=api_key)
        print("✅ AI Bot initialized successfully!")
        print("\nCommands:")
        print("- Type 'quit' to exit")
        print("- Type 'debug' to see sentiment analysis")
        print("- Type anything else to chat!")
        print("\n")
        
        debug_mode = False
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("\n🤖 Bot: Thank you for chatting with me! Take care, and remember I'm always here when you need support! 💙")
                break
            
            if user_input.lower() == 'debug':
                debug_mode = not debug_mode
                status = "ON" if debug_mode else "OFF"
                print(f"\n🔧 Debug mode: {status}")
                continue
            
            if not user_input:
                continue
            
            # Get response from bot
            print("\n🤖 Bot: ", end="", flush=True)
            
            if debug_mode:
                sentiment, response = bot.chat(user_input)
                print(f"[Sentiment: {sentiment.upper()}] {response}")
            else:
                response = bot.chat_simple(user_input)
                print(response)
            
            print()
            
    except Exception as e:
        print(f"❌ Error initializing bot: {str(e)}")
        print("Please check your OpenAI API key and internet connection.")

if __name__ == "__main__":
    main() 