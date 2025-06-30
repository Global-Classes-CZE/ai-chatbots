# Lesson 7: Product Search Agent with Vector Store

This lesson shows how to build a product search agent that uses Pinecone vector store to find products by their dimensions and other attributes.

## Files Overview

- `product_agent.py` - The main agent that handles user queries
- `process_products.py` - Script to process products and upload to Pinecone
- `show_products.py` - Script to view what's in the vector store

## How This Shit Works

### 1. Product Processing & Indexing

```python
# process_products.py loads products and creates these fields:
{
    "id": "prod_123",
    "name": "Product Name",
    "price": 69.99,
    "dimensions": {
        "length": 42.0,  # in cm
        "width": 13.37,
        "height": 99.9
    },
    "category": ["Toys", "Action Figures", "Collectibles"],
    "description": "An awesome product..."
}

# Each product gets:
1. Embedding vector from its text (name + description)
2. Metadata with all the numerical fields
```

### 2. Pinecone Vector Store

The vector store has two parts:
- **Vectors**: The embeddings of product text
- **Metadata**: All the numerical shit we can filter on

```python
# Example Pinecone query
index.query(
    vector=query_embedding,  # Semantic search
    filter={  # Metadata filtering
        "$and": [
            # Match ANY dimension > 80cm
            {"$or": [
                {"length": {"$gte": 80}},
                {"width": {"$gte": 80}},
                {"height": {"$gte": 80}}
            ]},
            # Match category
            {"category_l1": "toys"},
            # Match price
            {"price": {"$lte": 50.0}}
        ]
    }
)
```

### 3. Using the Agent

1. Start the agent:
```bash
python product_agent.py
```

2. Ask for products with constraints:
```
You: Show me toys larger than 80cm
Bot: Here are products that match...
```

3. View what's in the store:
```bash
python show_products.py
```

## Key Concepts

1. **Vector Search**: Find similar products by embedding
2. **Metadata Filtering**: Filter by numbers (price, size)
3. **Dimension Logic**:
   - "larger than X" -> ANY dimension > X
   - "smaller than X" -> ALL dimensions < X
   - "width > X" -> Only width > X

## Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your .env file:
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=your_index_name
```

## Common Issues

1. **Wrong Dimensions**: Make sure all dimensions are in centimeters
2. **Missing Metadata**: All numerical fields must exist in Pinecone
3. **Query Logic**: Use `$or` for "any dimension", `$and` for "all dimensions"

Let me know if you need any other details! 