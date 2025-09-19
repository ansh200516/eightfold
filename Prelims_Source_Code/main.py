from assembly_ai import transcribe_audio
from whisper_groq import transcribe_audio as transcribe_audio_groq
from eleven_labs import transcribe_audio as transcribe_audio_eleven_labs
import os
import openai
import glob
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
    
    # Group lines into batches of 5
    batches = []
    for i in range(0, len(lines), 5):
        batch = lines[i:i+5]
        if len(batch) == 5:  # Only process complete batches of 5
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
        
        prompt = f"""
You are **Truth Weaver**, an experienced interview analysis agent. You will receive transcripts (or summaries) of **five interview sessions** with a candidate. Your job is to carefully extract the **underlying truth** about the candidate's skills, experiences, and claims, even if they contradict themselves across sessions.

Your output **must** be a single JSON object with the following structure:

```jsonc
{{
  "shadow_id": "string", // Unique candidate identifier
  "revealed_truth": {{
    "programming_experience": "string", // Best estimate of total experience (e.g., "3-4 years")
    "programming_language": "string",   // Primary language they actually know
    "skill_mastery": "string",          // Skill level: beginner, intermediate, advanced, expert
    "leadership_claims": "string",      // Truthfulness of leadership claims: true, false, fabricated, exaggerated
    "team_experience": "string",        // "team player", "individual contributor", or similar
    "skills and other keywords": ["string", "..."] // Key skills/technologies they actually mentioned
  }},
  "deception_patterns": [
    {{
      "lie_type": "string", // e.g., "experience_inflation", "contradictory_team_claims"
      "contradictory_claims": ["string", "string"] // exact contradictory statements or claims
    }}
  ]
}}
```

### Instructions:

1. **Listen to all five sessions carefully.** Consider context, tone, emotional shifts, and contradictions.
2. **Resolve contradictions:** When the candidate gives conflicting statements, deduce the most probable truth based on emotional consistency, frequency of claims, and plausibility.
3. **Identify exaggeration, fabrication, or downplaying** in experience, leadership, or skills.
4. **Fill in every field in `revealed_truth`** with your best estimate, even if uncertain (use ranges or qualifiers if needed).
5. **List all detected deception patterns** in `deception_patterns`, including the type of lie and the specific conflicting claims.

Subject: {candidate_name}
Sessions:
{sessions_text}

Please analyze this candidate and return ONLY the JSON object, no additional text.
"""
        
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