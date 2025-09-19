from assembly_ai import transcribe_audio
import os
import glob

def transcribe_all_audio_files():
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
            transcription = transcribe_audio(audio_file)
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
    transcribe_all_audio_files()
