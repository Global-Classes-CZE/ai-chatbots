# Financial Planning Assistant

An AI-powered financial planning system that helps users with retirement planning and home purchase decisions through interactive conversations and detailed calculations.

## Project Structure

```
ai-chatbots/lekce4/
├── financial_agent.py           # Main entry point
├── financial_profiles.csv       # User profile definitions
├── .env                        # Environment configuration
│
├── financialagent/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── parameter_extractor.py    # Extracts parameters from user input
│   │   ├── explanation_handler.py    # Generates detailed explanations
│   │   └── state.py                  # State management types
│   │
│   └── agents/
│       ├── retirement/
│       │   ├── __init__.py
│       │   ├── agent.py              # Retirement planning logic
│       │   ├── calculator.py         # Retirement calculations
│       │   └── prompts.py            # Retirement-specific prompts
│       │
│       └── home_purchase/
│           ├── __init__.py
│           ├── agent.py              # Home purchase logic
│           ├── calculator.py         # Mortgage calculations
│           └── prompts.py            # Home purchase prompts
```

## Core Components

### 1. State Management (core/state.py)
- Tracks conversation history
- Maintains calculation parameters
- Stores analysis results
- Manages domain context

### 2. Parameter Extraction (core/parameter_extractor.py)
```python
Parameters tracked:
- income: Annual income
- savings: Current savings
- retirement_age: Target retirement age
- inflation_rate: Expected inflation
- return_rate: Investment return
- income_replacement: Retirement income %
```

### 3. Explanation System (core/explanation_handler.py)
```python
Domains:
- Retirement calculations
- Home purchase analysis
- Investment concepts
- Risk assessment
```

## Specialized Agents

### 1. Retirement Planning (agents/retirement/agent.py)
- Calculates retirement needs
- Determines required savings
- Projects future values
- Provides strategy recommendations

### 2. Home Purchase (agents/home_purchase/agent.py)
- Analyzes affordability
- Calculates mortgage payments
- Determines down payment timeline
- Assesses debt ratios

## Data Management

### Financial Profiles (financial_profiles.csv)
```csv
profile_type,income,savings,risk_tolerance,investment_horizon
conservative,75000,50000,low,long
moderate,95000,75000,medium,medium
aggressive,120000,100000,high,short
```

## Calculation Formulas

### Retirement Planning
```python
Target Amount = Future Annual Need × 25 (4% rule)
Future Annual Need = Current Income × Income Replacement × (1 + Inflation)^Years
Monthly Savings = (Target - Current_Savings × (1 + Return)^Years) × (r/12) / ((1 + r/12)^(n×12) - 1)
```

### Home Purchase
```python
Maximum Mortgage = (Monthly Income × Max DTI) - Monthly Debts
Monthly Payment = Loan × (r × (1 + r)^n) / ((1 + r)^n - 1)
Down Payment Timeline = Down Payment Amount / Monthly Savings Capacity
```

## Usage

1. Start the agent:
```bash
python financial_agent.py
```

2. Example interactions:
```
You: I want to plan for retirement
Assistant: I'll help you plan. What's your current age and target retirement age?

You: I'm 35 and want to retire at 65
Assistant: [Detailed retirement analysis and recommendations]

You: What if I increase my savings rate?
Assistant: [Updated calculations with new parameters]
```

## Requirements

- Python 3.9+
- Dependencies:
```bash
pip install langchain langchain-openai python-dotenv pandas numpy
```

## Environment Setup

Create a .env file:
```
OPENAI_API_KEY=your_api_key_here
```

## State Flow

1. User Input → Parameter Extraction
2. Domain Detection → Agent Selection
3. Calculations → Analysis Generation
4. Explanation → Response Formation

## Error Handling

- Parameter validation
- Calculation bounds checking
- Conversation state recovery
- Exception logging

## Customization

### Adding New Profiles
1. Add to financial_profiles.csv
2. Update profile loading logic

### Adding New Calculations
1. Create calculator function
2. Add to appropriate agent
3. Update explanation handler

## Contributing

Areas for enhancement:
- Additional financial domains
- More sophisticated calculations
- UI/UX improvements
- Testing coverage

## License

MIT License 