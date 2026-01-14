import requests
import re
import io
from pydub import AudioSegment
from app.voice_data import VALID_VOICE_IDS

def process_text_and_generate(full_text, base_voice, base_speed, mix_voice, api_base_url):
    """
    Parses text for markup and generates audio segments.
    Supports [voice:id] and [speed:float] tags.
    """
    
    api_base_url = api_base_url.rstrip('/')
    endpoint = f"{api_base_url}/v1/audio/speech"

    # Regex to find tags at the START of a line/paragraph
    # Matches: [voice:abc] OR [speed:1.2] followed by text
    # Note: This simple regex expects tags to be at the start of the line.
    markup_pattern = re.compile(r'^(?:\[(voice|speed):([^\]]+)\]\s*)+')

    lines = full_text.split('\n')
    combined_audio = AudioSegment.empty()
    
    # Initial State
    current_voice = base_voice
    current_speed = float(base_speed)
    
    # If a mix voice is provided in the UI, we combine it with the base
    # But markup overrides this.
    initial_mix = mix_voice

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for tags at start of line
        # We loop to handle multiple tags like [voice:a][speed:1.2]
        while True:
            match = markup_pattern.match(line)
            if not match:
                break
            
            # Extract full tag match (e.g. "[voice:a] ")
            tag_full = match.group(0)
            
            # Find all individual tags in this match
            individual_tags = re.findall(r'\[(voice|speed):([^\]]+)\]', tag_full)
            
            for tag_type, tag_value in individual_tags:
                if tag_type == 'voice':
                    # If user uses markup, we disable the UI mixing for this segment
                    # unless they explicitly write [voice:a+b]
                    current_voice = tag_value.strip()
                    initial_mix = None # Reset UI mixing on manual override
                elif tag_type == 'speed':
                    try:
                        current_speed = float(tag_value)
                    except:
                        pass

            # Remove the tags from the text line
            line = line[len(tag_full):].strip()

        if not line:
            continue

        # Construct Voice ID
        # If we have an active mix (from UI) and haven't overridden it with markup
        final_voice_id = current_voice
        if initial_mix and initial_mix != "none":
            final_voice_id = f"{current_voice}+{initial_mix}"

        # API Call
        try:
            print(f"--> Gen: '{line[:15]}...' | Voice: {final_voice_id} | Speed: {current_speed}")
            
            payload = {
                "model": "kokoro",
                "input": line,
                "voice": final_voice_id,
                "response_format": "wav",
                "speed": current_speed
            }
            
            response = requests.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                segment = AudioSegment.from_file(io.BytesIO(response.content), format="wav")
                combined_audio += segment
                # Pause logic: longer pause for periods, shorter for others
                if line.endswith('.'):
                    combined_audio += AudioSegment.silent(duration=400)
                else:
                    combined_audio += AudioSegment.silent(duration=150)
            else:
                print(f"API Error ({response.status_code}): {response.text}")
                
        except Exception as e:
            print(f"Error processing segment: {e}")
            raise Exception(f"Failed to connect to Kokoro API")

    return combined_audio