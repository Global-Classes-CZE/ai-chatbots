# Lesson 1: LangChain Chatbot with Dummy Responses

This lesson introduces **LangChain** - a powerful framework for building applications with large language models (LLMs). Instead of using real API calls, we'll create chatbots that return dummy responses, making it perfect for learning without API costs.

## What is LangChain?

LangChain is a framework designed to simplify the creation of applications using large language models. It provides:

- **Chains**: Link multiple components together
- **Prompts**: Template and manage model inputs  
- **Memory**: Maintain conversation context
- **Agents**: Let models use tools and make decisions
- **Custom LLMs**: Create your own language model implementations

## Files in this Lesson

### 1. `simple_langchain_bot.py` - Basic LangChain Example

A minimal implementation showing core LangChain concepts:
- Custom dummy LLM implementation
- Prompt templates
- Simple LLM chains

**Key Components:**
```python
# Custom LLM that returns dummy responses
class SimpleDummyLLM(LLM):
    def _call(self, prompt, **kwargs):
        return random.choice(responses)

# Prompt template for formatting input
template = "Human: {user_input}\nAssistant:"
prompt = PromptTemplate(template=template)

# Chain that connects LLM and prompt
chain = LLMChain(llm=llm, prompt=prompt)
```

**Run it:**
```bash
python simple_langchain_bot.py
```

### 2. `langchain_chatbot.py` - Advanced LangChain Chatbot

A more sophisticated implementation featuring:
- Conversation memory management
- Advanced dummy LLM with context awareness
- Conversation history tracking
- Memory clearing functionality

**Key Features:**
- **ConversationBufferMemory**: Keeps track of chat history
- **ConversationChain**: Manages the full conversation flow
- **Context-aware responses**: Different responses based on input type
- **Interactive commands**: `history`, `clear`, `quit`

**Run it:**
```bash
python langchain_chatbot.py
```

### 3. `llm_langchain_bot.py` - Real OpenAI Integration

A sentiment-aware support bot that uses the actual OpenAI API:
- **Real OpenAI API**: Uses GPT-3.5-turbo for responses
- **Sentiment Analysis**: Categorizes input as positive, negative, or neutral
- **Supportive Responses**: Tailored responses based on user's emotional state
- **API Key Required**: Needs OpenAI API key to function

**Key Behavior:**
- **Positive input** → Praise and encouragement
- **Negative input** → Support and help
- **Neutral/irrelevant** → Offer assistance and support

**Setup and Run:**
```bash
# 1. Set up your OpenAI API key
# Create a .env file with: OPENAI_API_KEY=your_key_here
# See env_setup_instructions.txt for detailed steps

# 2. Install additional dependencies
pip install openai python-dotenv

# 3. Run the bot
python llm_langchain_bot.py
```

### 4. `ai_powered_bot.py` - Fully AI-Powered Bot

A completely AI-driven bot that uses LLM for everything:
- **LLM Sentiment Analysis**: Uses OpenAI to analyze emotional tone
- **LLM Response Generation**: Generates unique responses for each input
- **No Predefined Responses**: Every response is created fresh by AI
- **No Keyword Matching**: Pure AI understanding and generation
- **Debug Mode**: See how the AI analyzes sentiment

**Key Features:**
- **Two-step AI process**: Sentiment analysis → Response generation
- **Dynamic responses**: Never the same response twice
- **Contextual understanding**: AI understands nuance and context
- **Debug mode**: Toggle to see sentiment classification

**Setup and Run:**
```bash
# Same setup as LLMLangChainBot
# 1. Create .env file with your OpenAI API key
# 2. Install dependencies: pip install openai python-dotenv
# 3. Run the bot
python ai_powered_bot.py
```

## Key LangChain Concepts Demonstrated

### 1. Custom LLM Implementation
```python
class DummyLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "dummy"
    
    def _call(self, prompt: str, **kwargs) -> str:
        # Your custom logic here
        return generate_response(prompt)
```

### 2. Conversation Memory
```python
memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="history"
)
```

### 3. Conversation Chains
```python
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)
```

### 4. Prompt Templates
```python
template = """You are a helpful assistant.
Human: {user_input}
Assistant:"""

prompt = PromptTemplate(
    input_variables=["user_input"],
    template=template
)
```

## Example Interaction

```
🤖 Welcome to Lesson 1: LangChain Chatbot Demo
==================================================
This chatbot uses LangChain with dummy responses.

You: Hello there!
🤖 Bot: Hello! It's great to meet you. How can I help you today?

You: What's the weather like?
🤖 Bot: That's an interesting question! Based on my analysis, I would say that this topic requires careful consideration.

You: history
📝 Conversation History:
1. You: Hello there!
2. Bot: Hello! It's great to meet you. How can I help you today?
3. You: What's the weather like?
4. Bot: That's an interesting question! Based on my analysis...
```

## Why Use Dummy Responses?

1. **Learning Focus**: Concentrate on LangChain concepts without API complexity
2. **No API Costs**: Practice without spending money on API calls
3. **Fast Development**: No need to set up API keys or handle rate limits
4. **Predictable Testing**: Consistent responses for testing your chain logic
5. **Offline Development**: Work without internet connectivity

## LangChain Benefits Demonstrated

- **Modularity**: Separate concerns (LLM, memory, chains)
- **Flexibility**: Easy to swap components (real LLM vs dummy)
- **Memory Management**: Automatic conversation history handling
- **Prompt Engineering**: Template-based prompt management
- **Error Handling**: Built-in error management and recovery

## Real-World Applications

Once you understand these concepts, you can easily replace the dummy LLM with real ones:

```python
# Instead of DummyLLM, use real LLMs:
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

llm = OpenAI(api_key="your-key")
# or
llm = ChatOpenAI(model="gpt-3.5-turbo")
```

## Next Steps

This lesson provides the foundation for:
- **Lesson 2**: Integrating real APIs (Azure OpenAI, OpenAI)
- **Lesson 3**: Advanced prompt engineering
- **Lesson 4**: Building specialized agents
- **Lesson 5**: Adding tools and external data sources

## Common LangChain Patterns

1. **Simple Chain**: `Prompt → LLM → Output`
2. **Conversation Chain**: `Memory + Prompt → LLM → Output + Memory Update`
3. **Sequential Chain**: `Chain1 → Chain2 → Chain3 → Final Output`
4. **Agent Pattern**: `LLM + Tools → Decision → Action → Result`

## Installation Requirements

### Option 1: Automated installation (Easiest)

**For macOS/Linux:**
```bash
cd ai-chatbots/lekce1
./install.sh
```

**For Windows:**
```cmd
cd ai-chatbots\lekce1
install.bat
```

### Option 2: Install from requirements file (Recommended)

```bash
# Navigate to lesson 1 directory
cd ai-chatbots/lekce1

# Install all dependencies
pip install -r requirements.txt

# OR install minimal dependencies only
pip install -r requirements-minimal.txt
```

### Option 2: Manual installation

```bash
# Essential packages for this lesson
pip install langchain>=0.1.0
pip install langchain-core>=0.1.0
pip install typing-extensions>=4.5.0
```

### Option 3: Using virtual environment (Best practice)

```bash
# Create virtual environment
python -m venv langchain-env

# Activate virtual environment
# On macOS/Linux:
source langchain-env/bin/activate
# On Windows:
# langchain-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### For real LLM integration (future lessons):
```bash
pip install openai
pip install langchain-openai
pip install python-dotenv
``` 