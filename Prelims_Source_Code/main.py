from assembly_ai import transcribe_audio
from whisper_groq import transcribe_audio as transcribe_audio_groq
from eleven_labs import transcribe_audio as transcribe_audio_eleven_labs
import os
import glob

def transcribe_all_audio_files(method):
    """Transcribe all audio files in the Evaluation set/audio directory"""
    audio_dir = "../Evaluation set/audio"
    output_file = "../transcribed.txt"
    
    audio_files = glob.glob(os.path.join(audio_dir, "*.mp3"))
    audio_files.sort()  
    transcriptions = []
    
    print(f"Found {len(audio_files)} audio files to transcribe...")
    
    for audio_file in audio_files:
        filename = os.path.basename(audio_file)
        print(f"Transcribing {filename}...")
        
        try:
            if method == "assembly_ai":
                transcription = transcribe_audio(audio_file)
            elif method == "whisper_groq":
                transcription = transcribe_audio_groq(audio_file)
            elif method == "eleven_labs":
                transcription = transcribe_audio_eleven_labs(audio_file)
            formatted_filename = filename.replace('.mp3', '.mp4')
            formatted_line = f"{formatted_filename}: {transcription}"
            transcriptions.append(formatted_line)
            
            print(f"✓ Successfully transcribed {filename}")
            
        except Exception as e:
            print(f"✗ Error transcribing {filename}: {str(e)}")
            formatted_filename = filename.replace('.mp3', '.mp4')
            formatted_line = f"{formatted_filename}: [ERROR: {str(e)}]"
            transcriptions.append(formatted_line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in transcriptions:
            f.write(line + '\n')
    
    print(f"\nAll transcriptions saved to {output_file}")
    print(f"Total files processed: {len(audio_files)}")

if __name__ == "__main__":
    transcribe_all_audio_files(method="eleven_labs")
