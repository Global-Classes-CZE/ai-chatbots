# Product Recommendation Chat API

An intelligent product recommendation system that handles various user intents, from product search to comparisons and support queries.

## 🏗️ Architecture Overview

### Core Components

#### 1. API Layer (`api.py`)
Main FastAPI application handling HTTP endpoints and state management.

```python
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str]
    products: List[Dict]
    criteria: Dict

class ChatState:
    conversations: Dict[str, Dict]  # Manages conversation state
```

Key endpoints:
- `/chat` - Main chat endpoint
- `/` - Health check

#### 2. Product Agent (`product_agent.py`)
Orchestrates the entire conversation flow and intent handling.

```python
class ProductAgent:
    def __init__(self, llm: AzureChatOpenAI)
    async def process_message(self, message: str, state: dict) -> dict
```

Main responsibilities:
- Message processing
- Intent classification routing
- State management
- Response generation

#### 3. Intent Classification (`intent_classifier.py`)
Determines user intent from messages.

```python
class UserIntent(Enum):
    REQUIREMENTS = "requirements and compatibility"
    FIRST_USE = "first time usage"
    COMPARISON = "product comparison"
    PURCHASE_NEW = "new purchase"
    PURCHASE_REPLACEMENT = "product replacement"
    PURCHASE_UPGRADE = "product upgrade"
    SUPPORT = "product support"
    WARRANTY = "warranty info"

class IntentClassifier:
    async def classify_intent(self, query: str) -> UserIntent
    def get_handler_name(self, intent: UserIntent) -> str
```

#### 4. Intent Resolution (`intent_resolver.py`)
Handles specific intents with specialized handlers.

Two main types of handlers:

##### A. Product Search Handlers
Require searching and finding new products:
- `handle_purchase()` - New product search
- `handle_upgrade()` - Finding better products
- `handle_replacement()` - Finding similar products

##### B. Context Handlers
Work with existing products/context:
- `handle_comparison()` - Compare selected products
- `handle_warranty()` - Warranty information
- `handle_support()` - Product support
- `handle_requirements()` - Product requirements
- `handle_first_use()` - Usage instructions

#### 5. Product Recommender (`product_recommendation.py`)
Handles product search and recommendations.

```python
class ProductRecommender:
    async def analyze_query(self, state: Dict) -> Dict
    def search_and_score_products(self, state: Dict) -> Dict
    def generate_recommendations(self, state: Dict) -> Dict
```

Key features:
- Query analysis
- Vector search using Pinecone
- Product scoring
- Recommendation generation

## 🔄 Main Flow

1. **Message Reception**
   ```
   HTTP Request -> API -> ProductAgent
   ```

2. **Intent Classification**
   ```
   ProductAgent -> IntentClassifier -> Determines Intent
   ```

3. **Intent Handling**
   
   A. Product Search Flow:
   ```
   IntentResolver
   ├── Analyze Query
   ├── Search Products (Pinecone)
   ├── Score Results
   └── Generate Recommendations
   ```

   B. Context Handling Flow:
   ```
   IntentResolver
   ├── Get Current Products
   ├── Process Intent-Specific Logic
   └── Generate Response
   ```

4. **Response Generation**
   ```
   Handler -> Format Response -> API Response
   ```

## 🎯 Intent Handling Details

### Product Search Intents

1. **PURCHASE_NEW**
```python
async def handle_purchase(self, state: Dict):
    # 1. Analyze query for criteria
    # 2. Search products in Pinecone
    # 3. Score and rank results
    # 4. Generate recommendations
```

2. **PURCHASE_UPGRADE**
```python
async def handle_upgrade(self, state: Dict):
    # 1. Extract current product features
    # 2. Search for better products
    # 3. Compare improvements
    # 4. Generate upgrade recommendations
```

### Context-Based Intents

1. **COMPARISON**
```python
async def handle_comparison(self, state: Dict):
    # 1. Get products from state
    # 2. Extract comparable features
    # 3. Generate detailed comparison
    # 4. Format response with markdown
```

2. **WARRANTY**
```python
async def handle_warranty(self, state: Dict):
    # 1. Get product from state
    # 2. Extract warranty info
    # 3. Generate warranty response
```

## 🔍 Product Search & Scoring

### Query Analysis
```python
async def analyze_query(self, state: Dict):
    # 1. Extract search terms
    # 2. Identify constraints
    # 3. Parse numeric values
    # 4. Return structured criteria
```

### Search Process
```python
def search_and_score_products(self, state: Dict):
    # 1. Build filter conditions
    # 2. Generate embeddings
    # 3. Query Pinecone
    # 4. Process results
    # 5. Score products
```

## 🔧 Setup & Configuration

### Environment Variables
```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=your_version
PINECONE_API_KEY=your_key
PINECONE_INDEX=your_index
```

### Dependencies 
fastapi
uvicorn
python-dotenv
langchain
langchain-openai
pinecone-client
pydantic
rich

## 🚀 Running the API

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
```

## 🐳 Docker Support

```bash
# Build and run with docker-compose
docker compose up --build

# Or run directly
docker build -t product-chat-api .
docker run -p 8001:8001 product-chat-api
```

## 📝 Logging

The API uses rich logging to track:
- Intent classification
- Product search results
- Handler execution
- Error tracking

Check logs with:
```bash
docker compose logs -f
```
```