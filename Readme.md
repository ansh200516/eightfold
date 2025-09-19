# Truth Weaver - AI-Powered Interview Deception Detection System

Link to repo: [https://github.com/ansh200516/eightfold]

## Team: Innov8

This project implements an AI-powered system called "Truth Weaver" that analyzes interview transcripts to detect deception patterns, contradictory claims, and reveal the underlying truth about candidates' skills and experiences.

## Project Overview

Truth Weaver is designed to process audio recordings of multiple interview sessions with job candidates and use advanced AI analysis to:

- **Detect Deception Patterns**: Identify contradictory statements across multiple interview sessions
- **Reveal Truth**: Extract the most likely accurate information about candidates' experience and skills
- **Categorize Claims**: Classify leadership claims, experience levels, and skill assertions
- **Generate Insights**: Provide structured analysis in JSON format for decision-making

## System Architecture

### High-Level Approach

```
Audio Files → Transcription → Batch Processing → AI Analysis → Structured Output
     ↓              ↓              ↓              ↓              ↓
   MP3/MP4     Text Extraction   Group by       GPT-4        JSON Results
   Files       (Multiple APIs)   Candidate    Analysis      (Truth + Lies)

```


### Core Components

1. **Multi-Provider Transcription Engine**
2. **Intelligent Text Processing Pipeline** 
3. **AI-Powered Deception Analysis**
4. **Structured Data Output System**

## 📁 Project Structure

```
TeamName_Innov8_3/
├── Prelims_Source_Code/           # Main application code
│   ├── main.py                    # Core orchestration logic
│   ├── prompt.py                  # AI prompt engineering
│   ├── assembly_ai.py             # AssemblyAI transcription
│   ├── whisper_groq.py           # Groq Whisper transcription
│   ├── eleven_labs.py            # ElevenLabs transcription
│   └── utils.py                  # Text processing utilities
├── Evaluation set/audio/          # Input audio files
├── logs/                         # Detailed transcription logs
├── PrelimsSubmission.json        # Final analysis results
├── raw.txt                       # Raw transcription output
└── transcribed.txt              # Processed transcription output
```

## Detailed Technical Approach

### 1. Multi-Provider Audio Transcription

**Why Multiple Providers?**
We implemented three different transcription services to ensure maximum accuracy and reliability:

#### Assembly AI Integration (`assembly_ai.py`)
```python
# Advanced transcription with detailed metadata
config = aai.TranscriptionConfig(punctuate=False)
transcript = aai.Transcriber(config=config).transcribe(audio_file)
```

**Features:**
- High-accuracy speech-to-text
- Confidence scores and language detection
- Word-level timestamps
- Comprehensive metadata logging

#### Groq Whisper Integration (`whisper_groq.py`)
```python
# Fast, cost-effective transcription
transcription = client.audio.transcriptions.create(
    file=(audio_file, file.read()),
    model="whisper-large-v3",
    response_format="verbose_json"
)
```

**Features:**
- OpenAI Whisper model via Groq
- Verbose JSON output format
- Language and duration detection
- Preprocessing for consistency

#### ElevenLabs Integration (`eleven_labs.py`)
```python
# Specialized voice transcription
transcription = elevenlabs.speech_to_text.convert(
    file=(audio_file, file.read()),
    model_id="scribe_v1",
    language_code="eng"
)
```

**Features:**
- Voice-optimized transcription
- Multiple language support
- Specialized for conversational audio

### 2. Intelligent Text Processing Pipeline

#### Contraction Expansion (`utils.py`)
Our sophisticated text processing system handles:

**Advanced Contraction Resolution:**
```python
def expand_contractions(text: str, use_spacy: bool = True) -> dict:
    # Handles ambiguous contractions like 's, 'd, 're
    # Uses spaCy for context-aware disambiguation
    # Falls back to heuristics when needed
```

**Key Features:**
- **Context-Aware Disambiguation**: Uses spaCy NLP to determine if "'s" means "is" or "has"
- **Past Participle Detection**: Identifies when "'d" should be "had" vs "would"
- **Comprehensive Coverage**: 150+ contraction patterns and informal speech patterns
- **Case Preservation**: Maintains original capitalization patterns

**Example Processing:**
```
Input:  "I'd check the logs. He's been working on it."
Output: "I would check the logs. He has been working on it."
```

#### Text Normalization
```python
def preprocess_text(text):
    # Convert to lowercase
    # Remove punctuation (preserve apostrophes for contractions)
    # Normalize whitespace
    # Ensure consistency across providers
```

### 3. Batch Processing Logic

#### Candidate Grouping Strategy
```python
# Group transcriptions by candidate (5 sessions each)
for i in range(0, len(lines), 5):
    batch = lines[i:i+5]
    if len(batch) == 5:  # Only process complete sets
        candidate_name = batch[0].split('_')[0]  # Extract from filename
        # Process as cohesive analysis unit
```

**Why Batches of 5?**
- Each candidate has exactly 5 interview sessions
- Allows for comprehensive contradiction detection
- Provides sufficient data for pattern analysis
- Enables cross-session consistency checking

### 4. AI-Powered Deception Analysis

#### Prompt Engineering (`prompt.py`)

Our sophisticated prompt guides GPT-4 to act as "Truth Weaver" - an expert interview analysis agent:

```python
prompt = f"""
You are **Truth Weaver**, an experienced interview analysis agent. 
You will receive transcripts of **five interview sessions** with a candidate. 
Your job is to carefully extract the **underlying truth** about the candidate's 
skills, experiences, and claims, even if they contradict themselves across sessions.
"""
```

**Key Analysis Dimensions:**

1. **Programming Experience Assessment**
   - Total years of experience
   - Primary programming language
   - Skill mastery level (beginner/intermediate/advanced/expert)

2. **Leadership Claims Verification**
   - Truthfulness assessment: true/false/fabricated/exaggerated
   - Team experience evaluation
   - Management vs. individual contributor roles

3. **Deception Pattern Detection**
   - Experience inflation
   - Skill exaggeration  
   - Contradictory team claims
   - Leadership fabrication

#### GPT-4 Analysis Configuration
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are Truth Weaver..."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1  # Low temperature for consistent analysis
)
```

**Why GPT-4?**
- Superior reasoning capabilities for complex contradiction detection
- Better context understanding across multiple sessions
- More reliable JSON output formatting
- Enhanced ability to infer underlying truth from conflicting statements

### 5. Structured Output Generation

#### JSON Schema Design
```json
{
  "shadow_id": "string",
  "revealed_truth": {
    "programming_experience": "string",
    "programming_language": "string", 
    "skill_mastery": "string",
    "leadership_claims": "string",
    "team_experience": "string",
    "skills and other keywords": ["array"]
  },
  "deception_patterns": [
    {
      "lie_type": "string",
      "contradictory_claims": ["statement1", "statement2"]
    }
  ]
}
```

##  Key Innovation: Cross-Session Contradiction Detection

### The Challenge
Traditional interview analysis examines single sessions in isolation. Our system's breakthrough is analyzing **consistency patterns across multiple sessions** to reveal deception.

### Our Solution
```python
# Extract candidate name from first session
first_line = batch[0]
candidate_name = first_line.split('_')[0]

# Format all 5 sessions for contextual analysis
sessions_text = "\n".join([
    f"• Session {i+1}: \"{line.split(': ', 1)[1]}\"" 
    for i, line in enumerate(batch)
])
```

**Pattern Recognition Examples:**

1. **Experience Inflation Detection:**
   ```
   Session 1: "I'm a seasoned DevOps engineer..."
   Session 5: "It was just a summer internship..."
   → DETECTED: experience_inflation
   ```

2. **Skill Contradiction Analysis:**
   ```
   Session 2: "I wrote all our policies from scratch..."
   Session 4: "I just deploy the YAML files he gives me..."
   → DETECTED: skill_inflation
   ```

3. **Leadership Claim Verification:**
   ```
   Session 1: "I was the Lead Architect..."
   Session 5: "I'm just a junior dev..."
   → DETECTED: leadership_fabrication
   ```

##  Advanced Features

### 1. Comprehensive Logging System
Every transcription is logged with full metadata:
```python
transcript_dict = {
    "service": "assembly_ai",
    "confidence": confidence_score,
    "language_code": detected_language,
    "audio_duration": duration,
    "words": word_level_data,
    "timestamp": processing_time,
    # ... extensive metadata
}
```

### 2. Error Handling & Resilience
```python
try:
    transcription = transcribe_audio(audio_file)
    # Process successfully
except Exception as e:
    # Log error but continue processing
    formatted_line = f"{filename}: [ERROR: {str(e)}]"
    transcriptions.append(formatted_line)
```

### 3. Provider Fallback Strategy
The system supports easy switching between transcription providers:
```python
if method == "assembly_ai":
    transcription = transcribe_audio(audio_file)
elif method == "whisper_groq":
    transcription = transcribe_audio_groq(audio_file)
elif method == "eleven_labs":
    transcription = transcribe_audio_eleven_labs(audio_file)
```

##  Results Analysis

### Example Detection: Atlas (Candidate)
```json
{
  "shadow_id": "atlas",
  "revealed_truth": {
    "programming_experience": "less than a year",
    "programming_language": "YAML",
    "skill_mastery": "beginner",
    "leadership_claims": "false"
  },
  "deception_patterns": [
    {
      "lie_type": "experience_inflation",
      "contradictory_claims": [
        "I'm a seasoned DevOps engineer...",
        "It was just a summer internship..."
      ]
    }
  ]
}
```

### Detection Accuracy Highlights
- **7 candidates analyzed** across 35 total interview sessions
- **Multiple deception patterns identified** per candidate
- **Detailed contradiction mapping** with exact quotes
- **Skill level assessment** from beginner to expert
- **Leadership claim verification** with evidence

## ⚙️ Installation & Setup

### Prerequisites
```bash
python 3.8+
OpenAI API key (for GPT-4)
AssemblyAI API key
Groq API key  
ElevenLabs API key
```

### Environment Configuration
```bash
# Create .env file
OPENAI_API_KEY=your_openai_key
ASSEMBLY_API_KEY=your_assembly_key
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### Dependencies
```bash
pip install openai assemblyai groq elevenlabs python-dotenv spacy
python -m spacy download en_core_web_sm
```

## 🎯 Usage

### Basic Execution
```bash
cd Prelims_Source_Code/
python main.py
```

This will:
1. Transcribe all audio files in `../Evaluation set/audio/`
2. Process transcriptions in batches of 5 (per candidate)
3. Analyze each candidate using GPT-4
4. Generate structured JSON output in `../PrelimsSubmission.json`

### Provider Selection
```python
# In main.py, change the transcription method:
transcribe_all_audio_files(method="assembly_ai")    # High accuracy
transcribe_all_audio_files(method="whisper_groq")   # Fast & efficient  
transcribe_all_audio_files(method="eleven_labs")    # Voice-optimized
```

## 🏆 Performance Characteristics

### Transcription Accuracy
- **AssemblyAI**: Highest accuracy, best for formal speech
- **Groq Whisper**: Best speed/cost ratio, good for clear audio
- **ElevenLabs**: Optimized for conversational interviews

### Analysis Speed
- **Per Candidate**: ~30-60 seconds (depending on transcription method)
- **Full Dataset**: ~5-10 minutes for 7 candidates
- **Rate Limits**: Handled gracefully with error recovery

### Resource Usage
- **Memory**: Efficient streaming processing
- **Storage**: Comprehensive logging (~1MB per audio file)
- **API Costs**: Optimized with batch processing

## Future Enhancements

### 1. Real-Time Analysis
- Stream processing for live interviews
- Immediate contradiction detection
- Real-time confidence scoring

### 2. Multi-Modal Analysis  
- Facial expression analysis
- Voice stress detection
- Gesture pattern recognition

### 3. Advanced ML Models
- Custom fine-tuned models for deception detection
- Industry-specific analysis patterns
- Historical candidate comparison

### 4. Interactive Dashboard
- Visual contradiction mapping
- Confidence timeline analysis
- Exportable reports

##  Contributing

This project demonstrates advanced AI application in HR technology, combining:
- **Multi-provider integration** for reliability
- **Sophisticated NLP processing** for accuracy  
- **Advanced prompt engineering** for insight extraction
- **Robust error handling** for production readiness

