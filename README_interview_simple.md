# AI Interview Simulator

An intelligent interview simulation system that conducts technical interviews for software engineering positions, focusing on Python and programming concepts.

## Features

- Dynamic topic-based questioning
- Adaptive follow-up questions
- Real-time response analysis
- Topic coverage tracking
- Emotional intelligence in responses
- Comprehensive interview summaries

## Usage

1. Start the interview:
```bash
python interview_simple.py
```

2. Example Interactions:
```
Interviewer: Could you explain how Python handles memory management?
You: [Your response]
Interviewer: [Follow-up based on your answer]

Interviewer: What's your experience with multithreading in Python?
You: [Your response]
```

3. Type 'quit' to end interview

## Technical Details

### Components

1. Topic Management:
   - CSV-based topic configuration
   - Dynamic topic selection
   - Coverage tracking for each topic

2. Response Analysis:
   - Factor-based evaluation
   - Context-aware follow-ups
   - Technical accuracy assessment

3. LangChain Integration:
   - GPT-4 for natural conversation
   - State management
   - Response generation

## Configuration

### Topics Structure (topics.csv)
```csv
type,id,content,factor
topic,T1,Python Basics,
factor,T1,Memory Management,understanding of GC
factor,T1,Data Types,knowledge of built-in types
```

## Requirements

- Python 3.9+
- LangChain
- OpenAI API key

## Environment Setup

1. Create .env file:
```
OPENAI_API_KEY=your_api_key_here
```

2. Install dependencies:
```bash
pip install langchain langchain-openai python-dotenv
```

## Features in Detail

### Topic Coverage
- Tracks understanding of key concepts
- Ensures comprehensive topic coverage
- Adapts questions based on responses

### Interview Flow
1. Introduction
2. Topic-based questions
3. Follow-up questions
4. Topic transitions
5. Final assessment

### Analysis
- Technical accuracy
- Communication skills
- Problem-solving approach
- Concept understanding

## Example Interview Session

```
Interviewer: Welcome to the technical interview. Let's start with Python basics.

Interviewer: Could you explain Python's garbage collection mechanism?

You: Python uses reference counting as its primary mechanism...

Interviewer: Interesting. How does Python handle circular references in that context?

[Interview continues with follow-up questions]
```

## Customization

### Adding New Topics
1. Update topics.csv
2. Add relevant factors
3. Define evaluation criteria

### Modifying Behavior
- Adjust temperature settings
- Modify system prompts
- Configure topic weights

## Error Handling

- Graceful conversation recovery
- State preservation
- Input validation
- Exception logging

## Contributing

Contributions welcome! Areas for improvement:
- Additional technical topics
- Enhanced evaluation metrics
- UI improvements
- Testing scenarios

## License

MIT License - Open for modification and distribution

## Notes

- Responses are evaluated in real-time
- Interview adapts to candidate's level
- Comprehensive logging for review
- Focus on technical accuracy and communication 