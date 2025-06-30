"""
Simple LangChain Chatbot - Beginner Version

This is a minimal example of using LangChain to create a chatbot
with dummy responses. Perfect for understanding the basics.
"""

from langchain.llms.base import LLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Optional, List, Any
import random

class SimpleDummyLLM(LLM):
    """A very simple dummy LLM for learning purposes"""
    
    @property
    def _llm_type(self) -> str:
        return "simple_dummy"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        """Return a random dummy response"""
        responses = [
            "That's an interesting point you've made!",
            "I see what you're getting at. Let me think about that.",
            "Thanks for sharing that with me. Here's my perspective:",
            "That's a great question! I'd say the answer depends on several factors.",
            "I find that topic quite fascinating. What made you think of it?"
        ]
        return random.choice(responses)

def create_simple_chatbot():
    """Create a simple LangChain chatbot"""
    
    # Create the dummy LLM
    llm = SimpleDummyLLM()
    
    # Create a simple prompt template
    template = """
    You are a helpful assistant. Please respond to the following message:
    
    Human: {user_input}
    Assistant:"""
    
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=template
    )
    
    # Create the chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain

def main():
    """Run the simple chatbot"""
    print("🤖 Simple LangChain Chatbot")
    print("=" * 30)
    print("Type 'quit' to exit\n")
    
    # Create the chatbot
    chatbot = create_simple_chatbot()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
            
        if not user_input:
            continue
        
        # Get response using LangChain
        try:
            response = chatbot.run(user_input=user_input)
            print(f"Bot: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main() 