import os
from dotenv import load_dotenv
from io import BytesIO
import requests
from elevenlabs.client import ElevenLabs
import re
import json
import logging
from datetime import datetime
from utils import expand_contractions, convert_words_to_dict, convert_utterances_to_dict
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)


def preprocess_text(text):
    """
    Preprocess text to remove punctuation (except apostrophes) and convert to lowercase.
    Preserves apostrophes for contraction expansion.
    """
    if not text:
        return text
    
    text = text.lower()
    
    # Remove punctuation but preserve apostrophes for contraction expansion
    text = re.sub(r"[^\w\s]", "", text)
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def transcribe_audio(audio_file):
    """
    Transcribe audio using Groq Whisper API and apply same processing as AssemblyAI.
    """
    
    with open(audio_file, "rb") as file:
        transcription = elevenlabs.speech_to_text.convert(
            file=(audio_file, file.read()),
            model_id="scribe_v1",
            language_code="eng"
        )
    
    raw_text = transcription.text
    
    # Step 1: Preprocess (remove punctuation except apostrophes, lowercase)
    preprocessed_text = preprocess_text(raw_text)
    
    # Step 2: Expand contractions (needs apostrophes to work properly)
    # expansion_result = expand_contractions(preprocessed_text, use_spacy=True) if preprocessed_text else {
    #     "expanded_text": None, "method": None, "replacements": [], "original_text": None
    # }
    
    # expanded_text = expansion_result["expanded_text"]
    # expansion_method = expansion_result["method"]
    # replacements_summary = expansion_result["replacements"]
    
    # Step 3: Remove apostrophes for final submission format compliance
    # final_text = remove_apostrophes(expanded_text)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"../logs/transcript_{timestamp}.json"
    
    transcript_dict = {
        "service": "eleven_labs",
        "model": "scribe_v1",
        "raw_text": raw_text,
        "text": preprocessed_text,
        "audio_file": audio_file,
        "timestamp": timestamp,
        "language": getattr(transcription, 'language', None),
        "duration": getattr(transcription, 'duration', None),
    }
    
    with open(log_filename, 'w', encoding='utf-8') as f:
        json.dump(transcript_dict, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Transcript logged to: {log_filename}")
    logger.info(f"Raw text: {raw_text}")
    logger.info(f"Preprocessed text: {preprocessed_text}")
    
    return preprocessed_text



if __name__ == "__main__":
    audio_file = "../Evaluation set/audio/atlas_2025_3.mp3"
    transcription = transcribe_audio(audio_file)
    print(transcription)
