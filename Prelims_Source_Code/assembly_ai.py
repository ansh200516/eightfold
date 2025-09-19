import assemblyai as aai
from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime
import logging
from utils import expand_contractions, convert_words_to_dict, convert_utterances_to_dict
load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_audio(audio_file):

  config = aai.TranscriptionConfig(
      punctuate=False,
      speech_model=aai.SpeechModel.slam_1
  )

  transcript = aai.Transcriber(config=config).transcribe(audio_file)

  if transcript.status == "error":
      raise RuntimeError(f"Transcription failed: {transcript.error}")

  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  log_filename = f"../logs/transcript_{timestamp}.json"


  original_text = getattr(transcript, 'text', None)
  expansion_result = expand_contractions(original_text, use_spacy=True) if original_text else {"expanded_text": None, "method": None, "replacements": [], "original_text": None}
  expanded_text = expansion_result["expanded_text"]
  expansion_method = expansion_result["method"]
  replacements_summary = expansion_result["replacements"]

  transcript_dict = {
      "id": getattr(transcript, 'id', None),
      "status": getattr(transcript, 'status', None),
      "language_confidence": getattr(transcript, 'language_confidence', None),
      "confidence": getattr(transcript, 'confidence', None),
      "summarization": getattr(transcript, 'summarization', None),
      "language_code": getattr(transcript, 'language_code', None),
      "language_detection": getattr(transcript, 'language_detection', None),
      "original_text": original_text,
      "expanded_text": expanded_text,
      "expansion_method": expansion_method,
      "expansion_replacements_summary": replacements_summary,
      "text": expanded_text,
      "words": convert_words_to_dict(getattr(transcript, 'words', None)),
      "utterances": convert_utterances_to_dict(getattr(transcript, 'utterances', None)),
      "audio_duration": getattr(transcript, 'audio_duration', None),
      "punctuate": getattr(transcript, 'punctuate', None),
      "format_text": getattr(transcript, 'format_text', None),
      "disfluencies": getattr(transcript, 'disfluencies', None),
      "multichannel": getattr(transcript, 'multichannel', None),
      "auto_highlights_result": getattr(transcript, 'auto_highlights_result', None),
      "audio_start_from": getattr(transcript, 'audio_start_from', None),
      "audio_end_at": getattr(transcript, 'audio_end_at', None),
      "filter_profanity": getattr(transcript, 'filter_profanity', None),
      "summary_type": getattr(transcript, 'summary_type', None),
      "chapters": getattr(transcript, 'chapters', None),
      "summary_model": getattr(transcript, 'summary_model', None),
      "summary": getattr(transcript, 'summary', None),
      "topics": getattr(transcript, 'topics', None),
      "sentiment_analysis": getattr(transcript, 'sentiment_analysis', None),
      "entity_detection": getattr(transcript, 'entity_detection', None),
      "entities": getattr(transcript, 'entities', None),
  }

  with open(log_filename, 'w', encoding='utf-8') as f:
      json.dump(transcript_dict, f, indent=2, ensure_ascii=False)

  logger.info(f"Transcript logged to: {log_filename}")
  logger.info(f"Expansion method used: {expansion_method}")
  
  return expanded_text

if __name__ == "__main__":
  audio_file = "../Evaluation set/audio/hyperion_2022_3.mp3"
  transcribe_audio(audio_file)