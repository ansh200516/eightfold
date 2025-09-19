from assembly_ai import transcribe_audio
from whisper_groq import transcribe_audio as transcribe_audio_groq
from eleven_labs import transcribe_audio as transcribe_audio_eleven_labs
import os
import openai
import glob
from prompt import prompt
import json

def transcribe_all_audio_files(method):
    """Transcribe all audio files in the Evaluation set/audio directory"""
    audio_dir = "../Evaluation set/audio"
    output_file = "../raw.txt"
    
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
    
def analysis(input_file):
    """Analyze transcriptions in batches of 5 and generate JSON output"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    batches = []
    for i in range(0, len(lines), 5):
        batch = lines[i:i+5]
        if len(batch) == 5:  
            batches.append(batch)
    
    print(f"Found {len(batches)} complete batches of 5 sessions each")
    
    all_results = []
    
    for batch_idx, batch in enumerate(batches):
        print(f"Processing batch {batch_idx + 1}/{len(batches)}...")
        
        # Extract candidate name from first line
        first_line = batch[0]
        candidate_name = first_line.split('_')[0]  # Extract name like "atlas", "eos", etc.
        
        # Format the batch for the prompt
        sessions_text = "\n".join([f"• Session {i+1}: \"{line.split(': ', 1)[1]}\"" for i, line in enumerate(batch)])
        

        
        try:
            # Make API call to OpenAI
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Truth Weaver, an expert interview analysis agent. Return only valid JSON as specified."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result_json = json.loads(response_text)
                all_results.append(result_json)
                print(f"✓ Successfully analyzed {candidate_name}")
            except json.JSONDecodeError as e:
                print(f"✗ JSON parsing error for {candidate_name}: {e}")
                print(f"Response was: {response_text[:200]}...")
                
        except Exception as e:
            print(f"✗ API error for {candidate_name}: {e}")
    
    # Save all results to PrelimsSubmission.json
    output_file = "../PrelimsSubmission.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ All analyses saved to {output_file}")
    print(f"Total candidates analyzed: {len(all_results)}")
    
    return all_results

if __name__ == "__main__":
    transcribe_all_audio_files(method="eleven_labs")
    analysis("../raw.txt")