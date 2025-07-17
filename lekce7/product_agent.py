# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================
# Type hints for better code documentation and IDE support
from typing import Dict, List, Tuple, Optional, TypedDict, Annotated, NotRequired, Union
# Dataclass for creating structured data objects
from dataclasses import dataclass, asdict
# Enum for creating enumerated constants
from enum import Enum
# SQLite database operations (currently not used but imported for potential future use)
import sqlite3
# Pinecone vector database for product search and similarity matching
import pinecone
from pinecone import ServerlessSpec, Pinecone
# LangChain Azure OpenAI integrations for embeddings and chat models
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
# LangChain message types for conversation handling
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
# LangChain prompt templates for structured LLM interactions
from langchain.prompts import ChatPromptTemplate, PromptTemplate
# Operating system utilities for environment variable access
import os
# Load environment variables from .env file
from dotenv import load_dotenv
# Numerical operations for vector manipulations
import numpy as np
# LangGraph for building conversation flows as state machines
from langgraph.graph import StateGraph, END
# JSON parsing and serialization
import json
# Pydantic for data validation and schema enforcement
from pydantic import BaseModel, Field
# Rich console for beautiful terminal output
from rich.console import Console
from rich.markdown import Markdown
# Logging for debugging and monitoring
import logging
# LangChain chains for combining LLM operations
from langchain.chains import LLMChain
# Pydantic validators for custom data validation
from pydantic import validator

# Initialize Rich console for pretty printing
console = Console()

# =============================================================================
# PYDANTIC MODELS FOR DATA VALIDATION
# =============================================================================

class Intent(BaseModel):
    """
    Represents a shopping intent with confidence scoring
    Used to classify what the user wants to do (search, buy, get details, etc.)
    """
    intent: str = Field(
        description="Type of shopping intent (e.g., SEARCH, DETAILS, PURCHASE)"
    )
    weight: float = Field(
        ge=0.0, le=1.0,  # Constraint: value must be between 0 and 1
        description="Confidence in this intent classification"
    )
    explanation: str = Field(
        description="Detailed explanation of why this intent was identified"
    )

class DimensionConstraint(BaseModel):
    """
    Handles product dimension filtering with flexible constraint types
    Can handle exact values, minimum/maximum ranges, or combinations
    """
    min: Optional[float] = Field(default=None, description="Minimum value in cm")
    max: Optional[float] = Field(default=None, description="Maximum value in cm")
    value: Optional[float] = Field(default=None, description="Exact value in cm")

class ProductCriteria(BaseModel):
    """
    Comprehensive product search criteria extracted from user queries
    Handles price, category, dimensions, weight, and other constraints
    """
    price_range: Optional[Dict[str, float]] = Field(
        default=None,
        description="Price constraints in USD"
    )
    category: Optional[str] = Field(
        default=None,
        description="Product category or department"
    )
    dimensions: Optional[Dict[str, Union[DimensionConstraint, float]]] = Field(
        default=None,
        description="Size requirements with min/max constraints per dimension"
    )
    weight: Optional[Dict[str, float]] = Field(
        default=None,
        description="Weight requirements in specified units"
    )
    explanation: str = Field(
        description="Reasoning behind the identified criteria"
    )

    @validator('dimensions')
    def validate_dimensions(cls, v):
        """
        Custom validator to normalize dimension inputs
        Converts simple numbers to DimensionConstraint objects
        Ensures consistent data structure for dimension handling
        """
        if v is None:
            return v
        result = {}
        for key, value in v.items():
            if isinstance(value, (int, float)):
                # Convert simple numbers to constraint objects
                result[key] = DimensionConstraint(value=float(value))
            elif isinstance(value, dict):
                # Convert dicts to constraint objects
                result[key] = DimensionConstraint(**value)
            else:
                result[key] = value
        return result

class QueryAnalysis(BaseModel):
    """
    Complete analysis result of a user's shopping query
    Combines intent classification with criteria extraction
    """
    intents: List[Intent] = Field(
        description="List of identified shopping intents"
    )
    criteria: ProductCriteria = Field(
        description="Extracted product search criteria"
    )

# =============================================================================
# PRODUCT INTENT ENUMERATION
# =============================================================================

class ProductIntent(Enum):
    """
    Comprehensive enumeration of product shopping intents
    Categorizes different types of shopping motivations and preferences
    Used for intent-based product scoring and recommendations
    """
    # Value-focused intents - how much user wants to spend
    BUDGET_CONSCIOUS = "Looking for affordable options"
    PREMIUM_QUALITY = "Seeking high-end, premium products"
    BEST_VALUE = "Wanting best value for money"
    
    # Usage-focused intents - how user plans to use the product
    BEGINNER_FRIENDLY = "Suitable for beginners/entry-level"
    PROFESSIONAL_USE = "For professional/heavy use"
    CASUAL_USE = "For occasional/casual use"
    
    # Feature-focused intents - what capabilities user wants
    FEATURE_RICH = "Seeking products with many features"
    SIMPLICITY = "Preferring simple, straightforward options"
    INNOVATIVE = "Looking for innovative/unique solutions"
    
    # Physical attributes - size, weight, durability requirements
    COMPACT = "Needs to be space-efficient"
    LIGHTWEIGHT = "Needs to be easily portable"
    DURABILITY = "Must be long-lasting/durable"
    
    # Experience-focused - user experience priorities
    EASE_OF_USE = "Must be user-friendly"
    PERFORMANCE = "Prioritizing high performance"
    RELIABILITY = "Must be dependable"
    
    # Specific needs - special circumstances
    GIFT = "Shopping for a gift"
    URGENT_NEED = "Need immediate solution"
    REPLACEMENT = "Looking to replace existing product"
    
    # Style/Aesthetic - appearance and design preferences
    DESIGN_FOCUSED = "Emphasizing aesthetics"
    TRADITIONAL = "Preferring classic/traditional style"
    MODERN = "Seeking contemporary design"
    
    # Environmental/Social - ethical considerations
    ECO_FRIENDLY = "Environmentally conscious choice"
    SUSTAINABLE = "Seeking sustainable options"
    ETHICAL = "Concerned with ethical production"
    
    # Special considerations - safety and compatibility
    SAFETY = "Prioritizing safety features"
    COMPATIBILITY = "Must work with existing items"

class IntentQuery:
    """
    Maps product intents to search query templates
    Used for intent-based product scoring and matching
    """
    def __init__(self, intent: ProductIntent, weight: float = 1.0):
        self.intent = intent
        self.weight = weight
        self.query_templates = self._get_query_templates()
    
    def _get_query_templates(self) -> List[str]:
        """
        Generate search queries that represent this intent
        Maps each intent to natural language descriptions for vector search
        """
        templates = {
            ProductIntent.BUDGET_CONSCIOUS: [
                "affordable quality product with good value",
                "budget-friendly option that meets basic needs",
                "cost-effective solution without compromising quality"
            ],
            ProductIntent.PREMIUM_QUALITY: [
                "high-end premium product with superior quality",
                "luxury product with exceptional craftsmanship",
                "top-tier professional grade product"
            ],
            # Note: Other intents would have similar template mappings
        }
        return templates.get(self.intent, ["general purpose product"])

# =============================================================================
# CONVERSATION STATE MANAGEMENT
# =============================================================================

class ConversationState(TypedDict):
    """
    TypedDict defining the complete state of a shopping conversation
    Tracks conversation history, user intents, search criteria, and recommendations
    Used by LangGraph to maintain state across conversation nodes
    """
    messages: List[Dict[str, str]]  # Complete conversation history
    current_intents: List[Dict]  # Currently identified shopping intents
    current_criteria: Dict  # Current product search criteria
    recommended_products: List[Dict]  # Products currently being recommended
    satisfaction_level: float  # User satisfaction score (0-1)
    purchase_intent: bool  # Whether user wants to make a purchase
    needs_clarification: bool  # Whether we need more information from user
    conversation_stage: str  # Current stage of the conversation flow
    # Optional fields that may not always be present
    filtered_products: NotRequired[List[str]]  # Products after filtering
    scored_products: NotRequired[List[Dict]]  # Products after scoring
    current_intent: NotRequired[Dict]  # Current classified intent
    identified_category: NotRequired[str]  # Identified product category

class ConversationIntent(Enum):
    """
    High-level conversation intents for routing conversation flow
    Determines which node in the conversation graph to execute next
    """
    SEARCH = "search_products"  # User wants to search/modify search
    PURCHASE = "make_purchase"  # User wants to buy
    DETAILS = "get_details"    # User wants more details about specific product
    IRRELEVANT = "cant_help"   # User's request is not shopping related

# =============================================================================
# PRODUCT DATA MODELS
# =============================================================================
    
class ProductNode(BaseModel):
    """
    Complete product representation with all attributes and scoring
    Used for internal product processing and scoring calculations
    """
    id: str
    name: str
    price: float
    category: List[str]
    dimensions: Dict[str, float] = Field(
        description="Product dimensions in cm",
        default_factory=lambda: {
            "length": None,
            "width": None,
            "height": None
        }
    )
    weight: Optional[float] = Field(
        description="Product weight in kg",
        default=None
    )
    description: str = Field(description="Product description")
    score: float  # Overall relevance score
    intent_matches: Dict[str, float]  # How well it matches each intent
    criteria_matches: Dict[str, bool]  # How well it meets criteria
    explanation: str  # Detailed explanation of recommendation
    confidence: float  # Confidence in recommendation (0-1)

class ProductRecommendation(BaseModel):
    """
    Product recommendation model for presenting results to users
    Simplified version of ProductNode optimized for user presentation
    """
    product_id: str = Field(description="Unique identifier of the product")
    name: str = Field(description="Product name")
    price: float = Field(description="Current price in USD")
    category: List[str] = Field(description="Category hierarchy")
    dimensions: Dict[str, float] = Field(
        description="Product dimensions in cm",
        default_factory=lambda: {
            "length": None,
            "width": None,
            "height": None
        }
    )
    weight: Optional[float] = Field(
        description="Product weight in kg",
        default=None
    )
    score: float = Field(ge=0.0, le=1.0, description="Overall match score")
    intent_matches: Dict[str, float] = Field(
        description="How well product matches each intent"
    )
    explanation: str = Field(
        description="Detailed explanation of why this product is recommended"
    )

# =============================================================================
# MAIN PRODUCT AGENT CLASS
# =============================================================================

class ProductAgent:
    """
    Main shopping assistant agent that handles conversation flow and product recommendations
    Integrates Azure OpenAI, Pinecone vector search, and LangGraph conversation management
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize the agent with all required services and configurations
        Sets up logging, Azure OpenAI connections, Pinecone, and conversation state
        """
        # =============================================================================
        # LOGGING SETUP
        # =============================================================================
        # Configure logging for debugging and monitoring
        self.logger = logging.getLogger("Fiddley")
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        # Add console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
        
        self.logger.debug("Initializing ProductAgent with debug mode ON...")
        
        # =============================================================================
        # ENVIRONMENT SETUP
        # =============================================================================
        # Load environment variables from .env file
        load_dotenv()
        
        # =============================================================================
        # AZURE OPENAI SETUP
        # =============================================================================
        # Initialize embeddings service for converting text to vectors
        self.logger.debug("Setting up Azure OpenAI embeddings...")
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        
        # Initialize chat model for natural language generation
        self.logger.debug("Setting up Azure OpenAI LLM...")
        self.llm = AzureChatOpenAI(
            azure_deployment="gpt-4o",
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0  # Deterministic responses for consistency
        )
        
        # =============================================================================
        # PINECONE VECTOR DATABASE SETUP
        # =============================================================================
        # Initialize Pinecone for vector-based product search
        self.logger.debug("Setting up Pinecone...")
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX")
        
        # =============================================================================
        # CONVERSATION STATE INITIALIZATION
        # =============================================================================
        # Initialize conversation state tracking
        self.logger.debug("Initializing conversation state...")
        self.state = self._init_state()
        
        # =============================================================================
        # CONVERSATION GRAPH CREATION
        # =============================================================================
        # Create the LangGraph conversation flow
        self.logger.debug("Creating conversation graph...")
        self.graph = self._create_graph()
        
        self.logger.debug("Initialization complete!")
    
    def _init_state(self) -> Dict:
        """
        Initialize the conversation state with default values
        Returns a dictionary that tracks the entire conversation context
        """
        return {
            "messages": [],  # Complete conversation history
            "current_intent": None,  # Current classified intent from user
            "current_intents": [],  # List of all identified intents
            "current_criteria": {},  # Current search criteria extracted from user
            "scored_products": [],  # Products that match current criteria
            "satisfaction_level": 0.0,  # User satisfaction metric
            "purchase_intent": False,  # Whether user wants to buy something
            "needs_clarification": False,  # Whether we need more info from user
            "conversation_stage": "start"  # Current stage in conversation flow
        }
    
    def _create_graph(self) -> StateGraph:
        """
        Create the conversation flow graph using LangGraph
        Defines the nodes and edges that control conversation routing
        """
        # Create workflow with our state schema
        workflow = StateGraph(ConversationState)
        
        # =============================================================================
        # NODE DEFINITIONS
        # =============================================================================
        # Add processing nodes to the workflow
        workflow.add_node("classify_intent", self.classify_intent)  # Determine what user wants
        workflow.add_node("analyze_query", self.analyze_query)  # Extract search criteria
        workflow.add_node("score_products", self.search_and_score_products)  # Find matching products
        workflow.add_node("generate_recommendations", self.generate_recommendations)  # Create response
        
        # =============================================================================
        # CONVERSATION FLOW EDGES
        # =============================================================================
        # Define conditional routing based on intent classification
        workflow.add_conditional_edges(
            "classify_intent",  # Starting node
            self.route_intent,  # Routing function
            {
                "search": "analyze_query",  # If search intent -> analyze what they're looking for
                "details": "generate_recommendations",  # If details intent -> show product info
                "purchase": END,  # If purchase intent -> end conversation
                "irrelevant": END  # If irrelevant -> end conversation
            }
        )
        
        # Define linear flow for search operations
        workflow.add_edge("analyze_query", "score_products")  # After analysis -> search products
        workflow.add_edge("score_products", "generate_recommendations")  # After search -> generate response
        
        # Set entry point for the workflow
        workflow.set_entry_point("classify_intent")
        
        # Compile and return the executable workflow
        return workflow.compile()
    
    def classify_intent(self, state: Dict) -> Dict:
        """
        Classify the user's intent from their message
        Determines whether they want to search, get details, purchase, or something irrelevant
        """
        self.logger.debug("Classifying user intent...")
        self.logger.debug(f"User message: {state['messages'][-1]['content']}")
        
        # =============================================================================
        # INTENT CLASSIFICATION PROMPT
        # =============================================================================
        # Create structured prompt for intent classification
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a shopping assistant. Classify the user's intent into one of these categories:
- SEARCH: User wants to find or browse products (including by size, dimensions, weight, etc.)
- DETAILS: User wants more information about specific products
- PURCHASE: User wants to buy something
- IRRELEVANT: Not related to shopping at all

Return ONLY a JSON object in this exact format (nothing else):
{
    "intent": "SEARCH/DETAILS/PURCHASE/IRRELEVANT",
    "confidence": 0.0 to 1.0,
    "explanation": "why this intent was chosen"
}

IMPORTANT: Always return valid JSON, even if the user's message contains profanity or is rude."""),
            HumanMessage(content=state["messages"][-1]["content"])
        ])
        
        try:
            # =============================================================================
            # LLM INVOCATION AND RESPONSE PROCESSING
            # =============================================================================
            # Get classification from LLM
            response = self.llm.invoke(prompt.format_messages())
            
            # Clean up response - remove markdown formatting if present
            content = response.content
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            # Parse the JSON response
            classification = json.loads(content)
            state["current_intent"] = classification
            
            return state
            
        except Exception as e:
            # =============================================================================
            # ERROR HANDLING AND FALLBACK
            # =============================================================================
            self.logger.error(f"Classification failed: {str(e)}")
            # Provide fallback classification if parsing fails
            state["current_intent"] = {
                "intent": "SEARCH",
                "confidence": 1.0,
                "explanation": "Fallback classification due to error"
            }
            return state
    
    def route_intent(self, state: Dict) -> str:
        """
        Route to appropriate node based on classified intent
        Returns the next node name for LangGraph to execute
        """
        return state["current_intent"]["intent"].lower()
    
    def _fallback_analysis(self, state: Dict) -> Dict:
        """
        Fallback analysis when normal query parsing fails
        Provides basic search intent and criteria when LLM processing errors occur
        """
        self.logger.debug("Using fallback analysis...")
        
        # Create minimal viable analysis
        state["current_intents"] = [{
            "intent": "SEARCH",
            "weight": 1.0,
            "explanation": "Fallback search intent"
        }]
        
        state["current_criteria"] = {
            "price_range": None,
            "category": None,
            "dimensions": None,
            "weight": None,
            "explanation": "Unable to parse specific criteria"
        }
        
        return state

    def analyze_query(self, state: Dict) -> Dict:
        """
        Analyze user query to extract shopping intents and search criteria
        Uses LLM to understand what the user is looking for and convert to structured data
        """
        self.logger.debug("Analyzing query for intents and criteria...")
        
        # =============================================================================
        # CONTEXT-AWARE QUERY ANALYSIS PROMPT
        # =============================================================================
        # Create prompt that considers conversation history for refinements vs new searches
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""Analyze the shopping query and determine if it's:
1. A refinement of previous search (updating size/price/etc. for same type of product)
2. A completely new search (different type of product)

Previous criteria: {json.dumps(state.get('current_criteria', {}), indent=2)}

Return a JSON object that matches this schema:
{json.dumps(QueryAnalysis.model_json_schema(), indent=2)}

Examples:
- "Show me smaller ones" -> Refinement, keep product type but update size
- "No, I want toys instead" -> New search, different product type
- "Make it under 10cm" -> Refinement, update size only
- "Actually, show me books" -> New search, different product type

IMPORTANT: For size constraints:
- "smaller than X" -> {{"dimensions": {{"max": X}}}}
- "larger than X" -> {{"dimensions": {{"min": X}}}}
- "width less than X" -> {{"dimensions": {{"width": X}}}}"""),
            # Include recent conversation context for better understanding
            *[AIMessage(content=m["content"]) if m["role"] == "assistant" else HumanMessage(content=m["content"]) 
              for m in state["messages"][-3:]], # Last 3 messages for context
            HumanMessage(content=state["messages"][-1]["content"])
        ])
        
        try:
            # =============================================================================
            # LLM PROCESSING AND VALIDATION
            # =============================================================================
            # Get analysis from LLM
            response = self.llm.invoke(prompt.format_messages())
            
            # Clean up response content (remove code blocks if present)
            content = response.content
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            # Parse and validate using Pydantic schema
            analysis = QueryAnalysis.model_validate_json(content)
            
            # =============================================================================
            # CRITERIA MERGING LOGIC
            # =============================================================================
            # Update state with validated analysis data
            state["current_intents"] = [intent.model_dump() for intent in analysis.intents]
            
            # Handle refinement vs new search logic
            if state.get("current_criteria") and "refine" in analysis.criteria.explanation.lower():
                self.logger.debug("Refining existing search criteria...")
                new_criteria = analysis.criteria.model_dump()
                old_criteria = state["current_criteria"]
                
                # Merge criteria: new values override old ones, preserve existing for unspecified
                merged = old_criteria.copy()
                for key, value in new_criteria.items():
                    if value is not None:
                        merged[key] = value
                state["current_criteria"] = merged
            else:
                # New search: replace all criteria
                self.logger.debug("Using new search criteria...")
                state["current_criteria"] = analysis.criteria.model_dump()
            
            # Print debug summary for monitoring
            self._print_analysis_summary(analysis)
            
            return state
            
        except Exception as e:
            # =============================================================================
            # ERROR HANDLING WITH SMART FALLBACK
            # =============================================================================
            self.logger.error(f"Analysis failed: {str(e)}")
            if 'response' in locals():
                self.logger.error(f"LLM response was: {response.content}")
            
            # Smart fallback for dimension-related queries
            if any(word in state["messages"][-1]["content"].lower() 
                   for word in ["cm", "meter", "inch", "foot", "smaller", "larger"]):
                state["current_criteria"] = {
                    "dimensions": {"max": 100.0},  # Default to 1 meter maximum
                    "explanation": "Fallback for dimension query"
                }
            return state
    
    def search_and_score_products(self, state: Dict) -> Dict:
        """
        Search Pinecone vector database for products matching user criteria
        Applies metadata filters for dimensions, price, category, etc.
        """
        self.logger.debug("Searching and scoring products...")
        
        # =============================================================================
        # FILTER CONSTRUCTION
        # =============================================================================
        # Extract criteria and build Pinecone filter conditions
        criteria = state.get("current_criteria", {})
        filter_parts = []
        filter_conditions = {}
        
        # =============================================================================
        # DIMENSION FILTERING LOGIC
        # =============================================================================
        # Handle complex dimension constraints (min/max/exact values)
        if criteria.get("dimensions"):
            dims = criteria["dimensions"]
            self.logger.debug(f"Dimension criteria: {dims}")
            
            dimension_filters = []
            for dim_name, constraint in dims.items():
                if isinstance(constraint, dict):
                    conditions = {"$exists": True}  # Ensure field exists
                    
                    # Handle "larger than X" queries - any dimension can be larger
                    if dim_name.lower() == "min":
                        min_val = constraint.get("min") or constraint.get("value")
                        if min_val:
                            # Create OR condition for any dimension being larger than threshold
                            dimension_filters.append({
                                "$or": [
                                    {"length": {"$gte": float(min_val)}},
                                    {"width": {"$gte": float(min_val)}},
                                    {"height": {"$gte": float(min_val)}}
                                ]
                            })
                    # Handle specific dimension constraints
                    else:
                        if constraint.get("min"):
                            conditions["$gte"] = float(constraint["min"])
                        if constraint.get("max"):
                            conditions["$lte"] = float(constraint["max"])
                        dimension_filters.append({dim_name: conditions})
            
            # Combine dimension filters with AND logic
            if dimension_filters:
                if len(dimension_filters) > 1:
                    filter_parts.append({"$and": dimension_filters})
                else:
                    filter_parts.extend(dimension_filters)
        
        # =============================================================================
        # CATEGORY FILTERING
        # =============================================================================
        # Search across multiple category levels for flexibility
        if criteria.get("category"):
            category = criteria["category"].lower()
            self.logger.debug(f"Searching for category: {category}")
            filter_parts.append({
                "$or": [
                    {"category_l1": category},  # Top-level category
                    {"category_l2": category},  # Second-level category
                    {"category_l3": category},  # Third-level category
                    {"category_l4": category}   # Fourth-level category
                ]
            })
        
        # =============================================================================
        # PRICE FILTERING
        # =============================================================================
        # Handle price range constraints
        if criteria.get("price_range"):
            price_range = criteria["price_range"]
            self.logger.debug(f"Price criteria: {price_range}")
            
            price_conditions = {"$exists": True}
            if price_range.get("min"):
                price_conditions["$gte"] = float(price_range["min"])
            if price_range.get("max"):
                price_conditions["$lte"] = float(price_range["max"])
            
            filter_parts.append({"price": price_conditions})
        
        # =============================================================================
        # FILTER COMBINATION
        # =============================================================================
        # Combine all filters with AND logic
        if filter_parts:
            filter_conditions = {"$and": filter_parts}
        
        self.logger.debug(f"Filter conditions: {json.dumps(filter_conditions, indent=2)}")
        
        # =============================================================================
        # VECTOR SEARCH EXECUTION
        # =============================================================================
        # Generate embedding for semantic search
        query_text = state["messages"][-1]["content"]
        query_embedding = self.embeddings.embed_query(query_text)
        
        # Execute search with error handling and fallback
        try:
            # Check index statistics for debugging
            stats = self.pc.Index(self.index_name).describe_index_stats()
            self.logger.debug(f"Total products in index: {stats.total_vector_count}")
            
            # Perform vector search with metadata filters
            results = self.pc.Index(self.index_name).query(
                vector=query_embedding,
                filter=filter_conditions,
                top_k=5,  # Return top 5 matches
                include_metadata=True
            )
            
            self.logger.debug(f"Found {len(results.matches)} matching products")
            
            # =============================================================================
            # FALLBACK SEARCH STRATEGY
            # =============================================================================
            # If no results, try removing dimension filters (they may be too restrictive)
            if len(results.matches) == 0:
                self.logger.debug("No products found with current filters")
                # Remove dimension-related filters and retry
                filter_conditions = {k: v for k, v in filter_conditions.items() 
                                  if not any(d in str(v) for d in ["length", "width", "height"])}
                self.logger.debug(f"Retrying without dimension filters: {json.dumps(filter_conditions, indent=2)}")
                results = self.pc.Index(self.index_name).query(
                    vector=query_embedding,
                    filter=filter_conditions if filter_conditions else None,
                    top_k=5,
                    include_metadata=True
                )
                self.logger.debug(f"Found {len(results.matches)} products without dimension filters")
            
            # =============================================================================
            # RESULT PROCESSING
            # =============================================================================
            # Convert Pinecone results to our internal format
            state["scored_products"] = [
                {
                    "id": match.id,
                    "score": match.score,  # Similarity score from vector search
                    "metadata": match.metadata  # Product attributes
                }
                for match in results.matches
            ]
            
        except Exception as e:
            # Handle search errors gracefully
            self.logger.error(f"Search failed: {str(e)}")
            state["scored_products"] = []
        
        return state
    
    def _print_analysis_summary(self, analysis: QueryAnalysis) -> None:
        """
        Print debug summary of query analysis results
        Helps with debugging and monitoring the analysis quality
        """
        self.logger.debug("Query Analysis Summary:")
        for intent in analysis.intents:
            self.logger.debug(f"Intent: {intent.intent} (confidence: {intent.weight})")
            self.logger.debug(f"Explanation: {intent.explanation}")
        self.logger.debug(f"Criteria: {analysis.criteria.model_dump_json(indent=2)}")

    def generate_recommendations(self, state: Dict) -> Dict:
        """
        Generate natural language product recommendations using LLM
        Takes scored products and creates user-friendly explanations
        """
        # =============================================================================
        # RECOMMENDATION GENERATION PROMPT
        # =============================================================================
        # Create messages for recommendation generation
        messages = [
            SystemMessage(content="""You are a shopping assistant. Generate product recommendations based on the provided 
            intents, criteria, and available products. Focus on explaining why each product matches the user's needs."""),
            HumanMessage(content=f"""
            User intents: {json.dumps(state['current_intents'], indent=2)}
            Search criteria: {json.dumps(state['current_criteria'], indent=2)}
            Available products: {json.dumps(state['scored_products'], indent=2)}
            
            Generate recommendations that explain how each product matches the user's requirements.
            Focus especially on any specified dimensions, categories, or other criteria.
            """)
        ]
        
        try:
            # =============================================================================
            # LLM RECOMMENDATION GENERATION
            # =============================================================================
            # Generate personalized recommendations
            response = self.llm.invoke(messages)
            
            # Format response with helpful follow-up question
            recommendations = f"""Here are some products that match your requirements:

{response.content}

Would you like more details about any of these products?"""
            
            # =============================================================================
            # CONVERSATION STATE UPDATE
            # =============================================================================
            # Add assistant response to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": recommendations
            })
            
            return state
            
        except Exception as e:
            # =============================================================================
            # ERROR HANDLING
            # =============================================================================
            self.logger.error(f"Failed to generate recommendations: {str(e)}")
            # Provide helpful fallback message
            state["messages"].append({
                "role": "assistant",
                "content": "I apologize, but I had trouble finding matching products. Could you try rephrasing your requirements?"
            })
            return state
    
    def chat(self):
        """
        Main conversation loop that handles user interaction
        Manages the complete chat session from start to finish
        """
        self.logger.debug("Starting chat session...")
        console.print("\n[bold blue]🤖 Hi! I'm Fiddley, your shopping assistant. How can I help you today?[/bold blue]")
        
        # =============================================================================
        # MAIN CONVERSATION LOOP
        # =============================================================================
        while True:
            # =============================================================================
            # USER INPUT HANDLING
            # =============================================================================
            # Get user input with basic validation
            user_input = input("\nYou: ").strip()
            self.logger.debug(f"Received user input: {user_input}")
            
            # Handle exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                console.print("\n[bold blue]👋 Thanks for shopping! Have a great day![/bold blue]")
                break
            
            # =============================================================================
            # CONVERSATION PROCESSING
            # =============================================================================
            # Add user message to conversation history
            self.logger.debug("Adding message to conversation history...")
            self.state["messages"].append({"role": "user", "content": user_input})
            
            try:
                # =============================================================================
                # GRAPH EXECUTION
                # =============================================================================
                # Process user input through conversation graph
                self.logger.debug("Invoking conversation graph...")
                self.state = self.graph.invoke(dict(self.state))  # Convert to dict for LangGraph
                
                # =============================================================================
                # RESPONSE DISPLAY
                # =============================================================================
                # Find and display the latest assistant response
                self.logger.debug("Finding latest assistant message...")
                latest_message = next((m for m in reversed(self.state["messages"]) 
                                    if m["role"] == "assistant"), None)
                if latest_message:
                    console.print(f"\n[bold blue]🤖 Fiddley:[/bold blue]")
                    console.print(Markdown(latest_message["content"]))
                
                # =============================================================================
                # CONVERSATION TERMINATION CHECK
                # =============================================================================
                # End conversation if user wants to purchase
                if self.state["purchase_intent"]:
                    self.logger.debug("Purchase intent detected, ending conversation...")
                    break
                    
            except Exception as e:
                # =============================================================================
                # ERROR HANDLING AND RECOVERY
                # =============================================================================
                self.logger.error(f"Error in chat loop: {str(e)}", exc_info=True)
                console.print(f"\n[bold red]🤖 Oops! Something went wrong: {str(e)}[/bold red]")
                console.print("Let's try again!")

    def identify_category(self, state: Dict) -> Dict:
        """
        Identify product category from user query (currently unused but available)
        Could be used for category-specific processing in future versions
        """
        self.logger.debug("Identifying product category...")
        
        # =============================================================================
        # CATEGORY IDENTIFICATION PROMPT
        # =============================================================================
        # Create prompt for category identification
        prompt = PromptTemplate(
            template="""Based on the user's query, identify the most likely product category.
            
            User query: {query}
            Previous context: {context}
            
            Return a JSON object with:
            {
                "category": "identified category",
                "confidence": 0.0 to 1.0,
                "explanation": "why this category was chosen"
            }
            """,
            input_variables=["query", "context"]
        )
        
        # Create LLM chain for category identification
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # =============================================================================
        # CONTEXT PREPARATION
        # =============================================================================
        # Build context from recent conversation history
        context = "\n".join([
            f"{m['role']}: {m['content']}" 
            for m in state["messages"][:-1]
        ])
        
        # =============================================================================
        # CATEGORY IDENTIFICATION EXECUTION
        # =============================================================================
        # Execute category identification
        response = chain.run({
            "query": state["messages"][-1]["content"],
            "context": context
        })
        
        try:
            # Parse and store category identification results
            result = json.loads(response)
            state["current_category"] = result["category"]
            state["category_confidence"] = result["confidence"]
            
            self.logger.debug(f"Identified category: {result['category']} (confidence: {result['confidence']})")
            self.logger.debug(f"Explanation: {result['explanation']}")
            
            return state
            
        except Exception as e:
            # Handle category identification errors
            self.logger.error(f"Category identification failed: {str(e)}")
            state["current_category"] = None
            state["category_confidence"] = 0.0
            return state

# =============================================================================
# MAIN EXECUTION FUNCTION
# =============================================================================

def main():
    """
    Main entry point for the application
    Creates and starts the product agent with debug mode enabled
    """
    # Create agent instance with debug logging enabled
    agent = ProductAgent(debug=True)
    # Start the interactive chat session
    agent.chat()

# =============================================================================
# SCRIPT EXECUTION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main() 