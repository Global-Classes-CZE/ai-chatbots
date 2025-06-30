"""
Lesson 1: LangChain Chatbot with Dummy Responses

This lesson introduces LangChain basics by creating simple chatbots
that use dummy/mock responses instead of real API calls.

Key concepts covered:
- Custom LLM implementation
- LangChain chains and prompts
- Conversation memory
- Basic chatbot architecture
"""

from .simple_langchain_bot import SimpleDummyLLM, create_simple_chatbot
from .langchain_chatbot import DummyLLM, LangChainChatbot
from .llm_langchain_bot import LLMLangChainBot, SentimentAnalyzer, OpenAIClient
from .ai_powered_bot import AIPoweredBot

__all__ = [
    'SimpleDummyLLM',
    'create_simple_chatbot', 
    'DummyLLM',
    'LangChainChatbot',
    'LLMLangChainBot',
    'SentimentAnalyzer',
    'OpenAIClient',
    'AIPoweredBot'
] 