# Building LangGraph Agents - A Comprehensive Guide

This guide explains how to build conversational AI agents using LangGraph and LangChain. It covers core concepts, components, and patterns for creating flexible, stateful agents.

## Core Components of an Agent

### 1. State Management
```python
from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    messages: List          # Conversation history
    context: Dict          # Current context/domain
    parameters: Dict       # Extracted parameters
    analysis: Dict         # Analysis results
    current_step: str      # Current workflow step
```

### 2. Graph Components
```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# Basic graph structure
builder = StateGraph(AgentState)
builder.add_node("process_input", process_input)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "process_input")
```

## Essential Building Blocks

### 1. Tools Definition
```python
def example_tool(param1: str, param2: int) -> Dict:
    """Tools must have type hints and docstrings"""
    return {"result": "processed"}

tools = [
    example_tool,
    another_tool
]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)
```

### 2. Conditional Edges
```python
def route_condition(state: AgentState) -> str:
    """Route to next node based on state"""
    if "calculation" in state["context"]:
        return "calculator"
    return "END"

builder.add_conditional_edges(
    "process_input",
    route_condition,
    {
        "calculator": "calculate",
        "END": END
    }
)
```

### 3. System Messages
```python
from langchain_core.messages import SystemMessage

sys_msg = SystemMessage(content="""You are a helpful assistant that can:
1. [Capability 1]
2. [Capability 2]

Always: [Behavior rules]
Never: [Restrictions]""")
```

## Common Agent Patterns

### 1. Intent Classification
```python
def classify_intent(state: AgentState) -> Dict:
    """Determine user's intent"""
    intent_prompt = SystemMessage(content="""
    RESPOND WITH ONE WORD from: [list of intents]
    Message: {user_message}
    """)
    response = llm.invoke([intent_prompt])
    return {"intent": response.content}
```

### 2. Parameter Extraction
```python
def extract_parameters(state: AgentState) -> Dict:
    """Extract parameters from user message"""
    extraction_prompt = SystemMessage(content="""
    Extract parameters as JSON:
    Message: {message}
    Parameters: [list parameters]
    """)
    return {"parameters": extracted_params}
```

### 3. Response Generation
```python
def generate_response(state: AgentState) -> Dict:
    """Generate contextual response"""
    context = state["context"]
    analysis = state["analysis"]
    
    response_prompt = SystemMessage(content="""
    Based on:
    Context: {context}
    Analysis: {analysis}
    
    Generate response that: [requirements]
    """)
    return {"messages": [response]}
```

## Workflow Patterns

### 1. Basic Flow
```
User Input → Intent Classification → Parameter Extraction → Processing → Response
```

### 2. Analysis Flow
```
User Input → Analysis → Intermediate State → Response Generation → Output
```

### 3. Tool-based Flow
```
User Input → Tool Selection → Tool Execution → Result Processing → Response
```

## State Management Patterns

### 1. Preserving Context
```python
def update_state(old_state: Dict, new_data: Dict) -> Dict:
    """Preserve important state while updating"""
    return {
        **old_state,
        "context": {**old_state["context"], **new_data},
        "messages": old_state["messages"] + [new_message]
    }
```

### 2. Analysis Storage
```python
def store_analysis(state: Dict, analysis: Dict) -> Dict:
    """Store analysis results for future reference"""
    return {
        **state,
        "analysis": {
            "timestamp": current_time,
            "results": analysis,
            "context": state["context"]
        }
    }
```

## Best Practices

1. **State Management**
   - Keep all relevant data in state
   - Use TypedDict for type safety
   - Preserve conversation history

2. **Tool Design**
   - Clear docstrings
   - Type hints
   - Error handling
   - Deterministic outputs

3. **Prompt Engineering**
   - Clear instructions
   - Examples
   - Constraints
   - Expected output format

4. **Error Handling**
   - State recovery
   - Graceful degradation
   - User feedback

## Example Implementation

```python
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# 1. Define tools
tools = [tool1, tool2, tool3]

# 2. Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)

# 3. Define system message
sys_msg = SystemMessage(content="System instructions...")

# 4. Create nodes
def process_input(state: MessagesState):
    """Process user input"""
    return {"messages": processed}

# 5. Build graph
builder = StateGraph(MessagesState)
builder.add_node("process", process_input)
builder.add_node("tools", ToolNode(tools))

# 6. Add edges
builder.add_edge(START, "process")
builder.add_conditional_edges(
    "process",
    tools_condition,
)
builder.add_edge("tools", "process")

# 7. Compile
graph = builder.compile()
```

## Testing Your Agent

1. **Basic Interaction Testing**
```python
state = {"messages": [sys_msg]}
response = graph.invoke(state)
```

2. **Tool Testing**
```python
test_inputs = [
    "use tool1 with param x",
    "calculate something",
]
```

3. **Edge Case Testing**
```python
error_cases = [
    "",  # Empty input
    "unknown command",  # Invalid input
    "quit",  # Exit commands
]
```

## Common Pitfalls

1. Not preserving state properly
2. Missing error handling
3. Unclear tool definitions
4. Overly complex routing logic
5. Insufficient prompt engineering

## Resources

- LangGraph Documentation
- LangChain Documentation
- OpenAI API Documentation
- Example Agents Repository 