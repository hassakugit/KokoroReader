import requests
import re
import io
from pydub import AudioSegment

# Default Voices list (Frontend uses this)
VOICES = {
    "Bella (American)": "af_bella",
    "Sarah (American)": "af_sarah",
    "Nicole (American)": "af_nicole",
    "Sky (American)": "af_sky",
    "Adam (American)": "am_adam",
    "Michael (American)": "am_michael",
    "Emma (British)": "bf_emma",
    "Isabella (British)": "bf_isabella",
    "George (British)": "bm_george",
    "Lewis (British)": "bm_lewis",
}

def process_text_and_generate(full_text, default_voice, api_base_url):
    """
    Parses text, splits by [voice:name], calls API for each chunk, 
    and stitches result.
    """
    
    # Ensure URL doesn't end with slash
    api_base_url = api_base_url.rstrip('/')
    
    # Construct the endpoint. Assuming OpenAI compatible endpoint.
    # If your API is different, change this URL.
    endpoint = f"{api_base_url}/v1/audio/speech"

    lines = full_text.split('\n')
    combined_audio = AudioSegment.empty()
    
    # Regex for markup: [voice:af_bella]
    markup_pattern = re.compile(r'^\[voice:([a-zA-Z0-9_]+)\]\s*(.*)')
    
    current_voice = default_voice
    valid_ids = list(VOICES.values())

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = markup_pattern.match(line)
        text_to_render = line

        if match:
            requested_voice = match.group(1)
            text_content = match.group(2)
            # Allow raw ID or friendly lookup (implied raw here)
            current_voice = requested_voice
            text_to_render = text_content

        if text_to_render:
            try:
                # Call the External API
                print(f"--> Sending to API [{current_voice}]: {text_to_render[:30]}...")
                
                payload = {
                    "model": "kokoro", # Standard placeholder
                    "input": text_to_render,
                    "voice": current_voice,
                    "response_format": "wav",
                    "speed": 1.0
                }
                
                response = requests.post(endpoint, json=payload, timeout=30)
                
                if response.status_code == 200:
                    # Convert bytes to AudioSegment
                    segment = AudioSegment.from_file(io.BytesIO(response.content), format="wav")
                    combined_audio += segment
                    # Add small pause between paragraphs
                    combined_audio += AudioSegment.silent(duration=300)
                else:
                    print(f"API Error ({response.status_code}): {response.text}")
                    
            except Exception as e:
                print(f"Connection Error processing segment: {e}")
                raise Exception(f"Failed to connect to Kokoro API at {api_base_url}. Is it running?")

    return combined_audio