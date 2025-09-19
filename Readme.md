# Audio Transcription Service

A Python-based audio transcription service that supports multiple transcription APIs including AssemblyAI, Groq Whisper, and ElevenLabs. The system processes audio files and generates standardized transcripts with comprehensive logging and text preprocessing capabilities.

## Key Features

The codebase implements several interesting techniques for professional audio processing:

- **Multi-provider transcription architecture** - Supports three different transcription services with a unified interface pattern
- **Advanced contraction expansion** using [regular expressions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions) and optional [spaCy NLP](https://spacy.io/) for linguistic disambiguation
- **Contextual text preprocessing** with intelligent handling of apostrophes and punctuation normalization
- **Comprehensive logging system** with timestamped JSON output for audit trails and debugging
- **File batch processing** using Python's [glob pattern matching](https://docs.python.org/3/library/glob.html) for directory traversal

## Technologies and Libraries

The project leverages several notable technologies that experienced developers will find interesting:

- **[AssemblyAI](https://www.assemblyai.com/)** - Enterprise-grade speech-to-text API with advanced features like sentiment analysis and entity detection
- **[Groq](https://groq.com/)** - High-performance inference for Whisper models with verbose JSON response format
- **[ElevenLabs](https://elevenlabs.io/)** - AI voice platform with speech-to-text capabilities using their Scribe v1 model
- **[spaCy](https://spacy.io/)** - Industrial-strength NLP library for intelligent contraction disambiguation
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** - Environment variable management for API key security

## Project Structure

```
├── Prelims_Source_Code/          # Core transcription modules
├── Evaluation set/
│   └── audio/                    # Audio files for processing (.mp3 format)
├── logs/                         # Timestamped transcription logs (JSON format)
├── old_logs/                     # Archive of previous processing runs
├── Bonus_Challenge/              # Additional challenge materials
└── transcribed.txt               # Final output with all transcriptions
```

**Interesting directories:**
- [`Prelims_Source_Code/`](./Prelims_Source_Code/) contains the modular transcription implementation with separate files for each service provider
- [`logs/`](./logs/) stores detailed JSON logs with metadata including confidence scores, language detection, and processing timestamps
- [`Evaluation set/audio/`](./Evaluation%20set/audio/) contains the source audio files organized with descriptive naming patterns

The [main.py](./Prelims_Source_Code/main.py) orchestrates the transcription process with error handling and file format standardization. The [utils.py](./Prelims_Source_Code/utils.py) module implements sophisticated contraction expansion algorithms that can disambiguate complex cases like "'s" (possessive vs. "is") and "'d" (past perfect vs. conditional) using either spaCy's linguistic analysis or fallback heuristics.

Each transcription service module ([assembly_ai.py](./Prelims_Source_Code/assembly_ai.py), [whisper_groq.py](./Prelims_Source_Code/whisper_groq.py), [eleven_labs.py](./Prelims_Source_Code/eleven_labs.py)) implements consistent preprocessing pipelines while leveraging the unique capabilities of their respective APIs.