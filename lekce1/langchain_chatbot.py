"""
Lesson 1: Simple LangChain Chatbot with Dummy Responses

This lesson demonstrates how to create a basic chatbot using LangChain
that returns dummy/mock responses without needing real API keys.
"""

from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.llms.base import LLM
from typing import Optional, List, Any
import random
import time

class DummyLLM(LLM):
    """
    A dummy LLM that returns predefined responses instead of calling a real API.
    This is useful for learning LangChain concepts without API costs.
    """
    
    def __init__(self):
        super().__init__()
        self.dummy_responses = [
            "That's an interesting question! Based on my analysis, I would say that this topic requires careful consideration.",
            "I understand your point. From my perspective, there are several ways to approach this matter.",
            "Thank you for sharing that with me. I find this topic quite fascinating and worth exploring further.",
            "That's a great observation! I think there are multiple dimensions to consider in this context.",
            "I appreciate you bringing this up. This is definitely something that deserves thoughtful discussion.",
            "Your question touches on an important aspect. Let me share some thoughts on this topic.",
            "This is a complex subject that I find quite intriguing. There are various factors to consider here.",
            "I see what you're getting at. This perspective opens up several interesting possibilities."
        ]
    
    @property
    def _llm_type(self) -> str:
        return "dummy"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate a dummy response based on the prompt.
        In a real implementation, this would call an actual LLM API.
        """
        # Simulate processing time
        time.sleep(0.5)
        
        # Simple logic to vary responses based on input
        if "?" in prompt:
            question_responses = [
                "That's a thoughtful question. Let me consider the various aspects involved.",
                "Great question! There are several ways to approach this topic.",
                "I'm glad you asked about this. It's an area that deserves careful exploration."
            ]
            return random.choice(question_responses)
        elif any(greeting in prompt.lower() for greeting in ["hello", "hi", "hey"]):
            greeting_responses = [
                "Hello! It's great to meet you. How can I help you today?",
                "Hi there! I'm excited to chat with you. What's on your mind?",
                "Hey! Welcome to our conversation. What would you like to discuss?"
            ]
            return random.choice(greeting_responses)
        elif any(word in prompt.lower() for word in ["bye", "goodbye", "see you"]):
            farewell_responses = [
                "Goodbye! It was wonderful chatting with you today.",
                "See you later! Thanks for the engaging conversation.",
                "Farewell! I hope we can chat again soon."
            ]
            return random.choice(farewell_responses)
        else:
            return random.choice(self.dummy_responses)

class LangChainChatbot:
    """
    A simple chatbot using LangChain with conversation memory.
    """
    
    def __init__(self):
        # Initialize the dummy LLM
        self.llm = DummyLLM()
        
        # Set up conversation memory
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history"
        )
        
        # Create a conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True  # Set to True to see the chain's internal workings
        )
        
        # System prompt to set the chatbot's personality
        self.system_message = """You are a helpful and friendly AI assistant. 
        You enjoy having conversations and are always eager to help users with their questions.
        You respond in a warm and engaging manner."""
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return a response using LangChain.
        """
        try:
            # Get response from the conversation chain
            response = self.conversation.predict(input=user_input)
            return response
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_conversation_history(self) -> List[dict]:
        """
        Get the conversation history from memory.
        """
        messages = self.memory.chat_memory.messages
        history = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": message.content})
        
        return history
    
    def clear_memory(self):
        """
        Clear the conversation memory.
        """
        self.memory.clear()
        print("Conversation memory cleared!")

def main():
    """
    Main function to run the LangChain chatbot demo.
    """
    print("🤖 Welcome to Lesson 1: LangChain Chatbot Demo")
    print("=" * 50)
    print("This chatbot uses LangChain with dummy responses.")
    print("It demonstrates:")
    print("- LangChain conversation chains")
    print("- Memory management")
    print("- Custom LLM implementation")
    print("- Conversation flow")
    print("=" * 50)
    print("\nCommands:")
    print("- Type 'quit' to exit")
    print("- Type 'history' to see conversation history")
    print("- Type 'clear' to clear conversation memory")
    print("- Type anything else to chat!")
    print("\n")
    
    # Initialize the chatbot
    chatbot = LangChainChatbot()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("\n🤖 Bot: Goodbye! Thanks for trying the LangChain chatbot demo.")
                break
            
            elif user_input.lower() == 'history':
                print("\n📝 Conversation History:")
                history = chatbot.get_conversation_history()
                if not history:
                    print("No conversation history yet.")
                else:
                    for i, entry in enumerate(history, 1):
                        role = "You" if entry["role"] == "user" else "Bot"
                        print(f"{i}. {role}: {entry['content']}")
                print()
                continue
            
            elif user_input.lower() == 'clear':
                chatbot.clear_memory()
                continue
            
            # Get response from chatbot
            print("\n🤖 Bot: ", end="")
            response = chatbot.chat(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\n🤖 Bot: Goodbye! Thanks for chatting with me.")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.\n")

if __name__ == "__main__":
    main() 