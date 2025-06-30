# Interest & Loan Calculator Agent

An interactive AI-powered loan calculator that helps users understand loan calculations, interest rates, and financial concepts.

## Features

- Calculate monthly loan payments
- Calculate total interest paid over loan term
- Explain financial concepts (APR, APY, amortization)
- Interactive Q&A about loan calculations
- Detailed breakdowns of payment structures

## Usage

1. Start the agent:
```bash
python interest_agent.py
```

2. Example commands:
```
Calculate loan for $200,000 at 5% for 30 years
Change interest rate to 4.5%
Explain why total interest is so high
What's the difference between APR and APY?
Show me monthly payments for $300,000 at 6% for 15 years
```

3. Type 'quit' to exit

## Technical Details

### Calculations

The agent uses standard loan amortization formulas:

- Monthly Payment = P * (r(1+r)^n) / ((1+r)^n - 1)
  - P = Principal
  - r = Monthly interest rate (annual rate / 12)
  - n = Total number of months

- Total Interest = (Monthly Payment * Number of Payments) - Principal

### Components

1. Core Calculator Functions:
   - `calculate_monthly_payment()`
   - `calculate_total_interest()`
   - `calculate_loan()`

2. LangChain Integration:
   - Uses GPT-4 for natural language understanding
   - Tool binding for calculations
   - Conversational state management

## Requirements

- Python 3.9+
- LangChain
- OpenAI API key (set in .env file)

## Environment Setup

Create a .env file with:
```
OPENAI_API_KEY=your_api_key_here
```

## Dependencies

```bash
pip install langchain langchain-openai python-dotenv
```

## Error Handling

- Validates input parameters
- Provides helpful error messages
- Maintains conversation state on errors
- Logs issues for debugging

## Examples

```
You: Calculate loan for $200,000 at 5% for 30 years
Assistant: Let me calculate that for you.

Monthly payment: $1,073.64
Total interest: $186,511.57
Total amount paid: $386,511.57

Here's why:
- The monthly interest rate is 5%/12 = 0.417%
- Over 30 years, you'll make 360 payments
- The formula accounts for compound interest
- Each payment goes partly to principal and partly to interest
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - Feel free to use and modify for your needs. 