# Financial Planning Agent

A conversational AI agent that helps users with retirement and home purchase planning. The agent understands different intents and maintains context throughout the conversation.

## Example Conversation

```
You: retire

AI: [Analyzes intent as "retirement" and starts new planning session]
    Shows initial retirement analysis with default parameters:
    - Current Age: 35
    - Retirement Age: 65
    - Annual Income: $95,000
    - Current Savings: $25,000
    - Target Amount: $4,611,798.70
    - Monthly Savings Needed: $3,624.26

You: Explain the calculation itself.

AI: [Detects "explanation" intent, provides detailed breakdown]
    Explains the calculation in plain English:
    1. What the numbers mean for you
    2. How they're calculated (4% rule, inflation adjustment)
    3. Why they matter
    4. What factors could change them

You: Change retirement age to 90

AI: [Detects "parameter_change" intent, updates calculations]
    Shows new analysis with updated parameters:
    - Retirement Age: 90 (changed from 65)
    - Years to retirement: 55 (increased from 30)
    - Target Amount: $9,656,082.32
    - Monthly Savings: $1,106.26
```

## How It Works

1. **Intent Detection**
   - The agent first determines the user's intent from their message
   - Main intents: retirement, home_purchase, explanation, parameter_change
   - Uses GPT-4 for intent classification

2. **Domain Management**
   - Maintains the current domain (retirement or home_purchase)
   - Domain persists across messages until explicitly changed
   - Explanations and parameter changes work within current domain

3. **State Graph**
   - Uses LangGraph for conversation flow
   - Routes messages based on intent:
     - explanation -> ExplanationHandler
     - parameter_change -> ParameterExtractor -> RetirementAgent
     - retirement/home_purchase -> ParameterExtractor -> Appropriate Agent

4. **Handlers**
   - **RetirementAgent**: Calculates retirement needs and savings plans
   - **ExplanationHandler**: Provides detailed explanations in plain English
   - **ParameterExtractor**: Identifies and updates parameters from user input

5. **State Management**
   - Maintains conversation history
   - Tracks current parameters and calculations
   - Preserves context between different intents

## Key Features

- Natural language parameter updates
- Detailed explanations on demand
- Context-aware responses
- Persistent domain state
- Real-time calculation updates