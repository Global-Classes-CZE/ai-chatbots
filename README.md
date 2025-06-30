# Interview System Architecture

## 1. Core Components

### HumanityManager (`humanity_manager.py`)
Orchestrates the human-centric aspects of the interview:

```python
class HumanityManager:
    def __init__(self, model):
        self.model = model
        self.analyzer = HumanityAnalyzer(model)
```

Key responsibilities:
- Processes responses through multiple humanity dimensions
- Enhances questions based on emotional state
- Manages interview flow adaptively
- Tracks emotional and cognitive patterns

### HumanityAnalyzer (`humanity_analyzer.py`)
Deep analysis of human responses:

```python
class HumanityAnalyzer:
    def analyze_emotional_content(self, response: str) -> Dict:
        # Analyzes:
        # - Emotional weight (0-1)
        # - Trauma indicators
        # - Emotional cues
        # - Key emotions
        # - Support needs
```

Key analysis dimensions:
1. **Emotional Analysis**
   - Emotional intensity
   - Trauma detection
   - Support needs
   - Emotional complexity

2. **Cognitive Analysis**
   - Mental load
   - Processing patterns
   - Fatigue indicators
   - Complexity handling

3. **Engagement Analysis**
   - Participation level
   - Response patterns
   - Topic investment
   - Interaction quality

### InterviewBot (`interview_bot.py`)
Main orchestrator managing the interview process:

```python
class InterviewBot:
    def __init__(self):
        self.humanity = HumanityManager(self.model)
        self.state = self.get_default_state()
```

Key features:
1. **State Management**
   ```python
   def get_default_state(self) -> State:
       return {
           "humanity": {
               "emotional": {...},
               "cognitive": {...},
               "engagement": {...},
               "formality": {...},
               "persona": {...}
           }
       }
   ```

2. **Response Processing**
   ```python
   def process_response(self, state: Dict) -> Dict:
       # 1. Factor analysis
       coverage = self.analyze_response(state["user_message"], current_topic)
       
       # 2. Emotional analysis
       processed_state = self.humanity.process_response(state, state["user_message"])
   ```

3. **Intent Analysis**
   ```python
   def analyze_intent(self, state: State) -> State:
       # Detects intents like:
       # - direct_response
       # - refuses_question
       # - asking_purpose
       # - seeking_clarification
       # - expressing_concern
   ```

## 2. Key Features

### Emotional Intelligence
1. **Trauma Detection**
```python
if any(word in message_lower for word in critical_words):
    processed_state["humanity"]["emotional"].update({
        "emotional_weight": 0.9,
        "trauma_indicators": True,
        "requires_support": True
    })
```

2. **Response Enhancement**
```python
def _build_enhancement_prompt(self, question: str, state: Dict) -> str:
    # Enhances based on:
    # - Emotional state
    # - Cognitive load
    # - Engagement level
    # - Formality needs
```

### Adaptive Behavior
1. **Question Generation**
```python
def _generate_base_question(self, state: Dict) -> Dict:
    # Adapts based on:
    # - Uncovered factors
    # - Emotional context
    # - Previous responses
    # - Support needs
```

2. **Topic Management**
```python
def check_topic_progress(self, state: Dict) -> Dict:
    # Tracks:
    # - Questions per topic
    # - Coverage progress
    # - Value assessment
    # - Topic exhaustion
```

## 3. Human Analysis Dimensions

### Emotional Analysis
```python
class EmotionalAnalysis(BaseModel):
    emotional_weight: float
    trauma_indicators: bool
    emotional_cues: List[str]
    key_emotions: List[str]
    requires_support: bool
    emotional_complexity: float
```

### Cognitive Analysis
```python
def assess_cognitive_load(self, response: str) -> Dict:
    return {
        "current_load": float,
        "complexity_indicators": List[str],
        "processing_patterns": Dict,
        "mental_effort_level": float,
        "fatigue_indicators": int
    }
```

### Engagement Analysis
```python
def calculate_engagement(self, response: str) -> Dict:
    return {
        "dimensions": {
            "elaboration": float,
            "investment": float,
            "emotional": float,
            "interactive": float,
            # ...more dimensions
        },
        "engagement_patterns": Dict
    }
```

## 4. Safety Features

1. **Critical Content Detection**
```python
critical_words = ['smrt', 'sebevražd', 'zemřel', 'zemřela', 'zabil', 'zabila']
```

2. **Support Triggers**
```python
if emotional["requires_support"]:
    # Trigger supportive response
    # Adjust approach
    # Monitor emotional state
```

3. **Topic Refusal Handling**
```python
def handle_topic_refusal(self, state: Dict) -> Dict:
    # Respects boundaries
    # Marks topics as sensitive
    # Adjusts approach
    # Moves to safer topics
```

This system is fucking smart because it:
1. Deeply analyzes human emotional states
2. Adapts in real-time to emotional needs
3. Handles trauma and sensitive topics carefully
4. Maintains professional research context while being emotionally intelligent
5. Uses multiple dimensions of human analysis for better understanding

Let me know if you need more details about any specific component!