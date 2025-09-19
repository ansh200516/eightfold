import os
import re
import json
from datetime import datetime
import logging
from groq import Groq
from dotenv import load_dotenv
from utils import expand_contractions, convert_words_to_dict, convert_utterances_to_dict

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

def preprocess_text(text):
    """
    Preprocess text to remove punctuation (except apostrophes) and convert to lowercase.
    This makes Groq output compatible with AssemblyAI format.
    """
    if not text:
        return text
    
    text = text.lower()
    
    text = re.sub(r"[^\w\s']", "", text)
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def transcribe_audio(audio_file):
    """
    Transcribe audio using Groq Whisper API and apply same processing as AssemblyAI.
    """
    
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_file, file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
        )
    
    raw_text = transcription.text
    
    preprocessed_text = preprocess_text(raw_text)
    
    expansion_result = expand_contractions(preprocessed_text, use_spacy=True) if preprocessed_text else {
        "expanded_text": None, "method": None, "replacements": [], "original_text": None
    }
    
    expanded_text = expansion_result["expanded_text"]
    expansion_method = expansion_result["method"]
    replacements_summary = expansion_result["replacements"]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"../logs/transcript_{timestamp}.json"
    
    transcript_dict = {
        "service": "groq_whisper",
        "model": "whisper-large-v3",
        "raw_text": raw_text,
        "preprocessed_text": preprocessed_text,
        "expanded_text": expanded_text,
        "expansion_method": expansion_method,
        "expansion_replacements_summary": replacements_summary,
        "text": expanded_text,  
        "audio_file": audio_file,
        "timestamp": timestamp,
        "language": getattr(transcription, 'language', None),
        "duration": getattr(transcription, 'duration', None),
    }
    
    with open(log_filename, 'w', encoding='utf-8') as f:
        json.dump(transcript_dict, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Transcript logged to: {log_filename}")
    logger.info(f"Expansion method used: {expansion_method}")
    logger.info(f"Raw text: {raw_text}")
    logger.info(f"Preprocessed text: {preprocessed_text}")
    logger.info(f"Final text: {expanded_text}")
    
    return expanded_text

if __name__ == "__main__":
    filename = "../Evaluation set/audio/atlas_2025_3.mp3"
    result = transcribe_audio(filename)
    print(result)
          