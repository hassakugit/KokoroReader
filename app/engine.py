import os
import torch
import numpy as np
import soundfile as sf
from kokoro import KPipeline
from pydub import AudioSegment
import io
import re

# Initialize Pipeline
# 'a' is for American English by default. 
# Kokoro will auto-download weights to the cache on first run.
device = 'cuda' if torch.cuda.is_available() else 'cpu'
PIPELINE = KPipeline(lang_code='a', device=device)

# Map of friendly names to voice codes (You can expand this list)
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

def get_voice_list():
    return VOICES

def generate_audio_segment(text, voice_key):
    """Generates audio for a specific text segment and returns pydub AudioSegment"""
    if not text.strip():
        return None
    
    # Generate audio (returns generator)
    generator = PIPELINE(text, voice=voice_key, speed=1, split_pattern=r'\n+')
    
    # Collect all audio pieces for this segment
    all_audio = []
    for _, _, audio in generator:
        all_audio.append(audio)
        
    if not all_audio:
        return None

    # Concatenate numpy arrays
    final_audio_np = np.concatenate(all_audio)
    
    # Convert buffer to Wav memory file for Pydub
    buffer = io.BytesIO()
    sf.write(buffer, final_audio_np, 24000, format='WAV')
    buffer.seek(0)
    
    return AudioSegment.from_wav(buffer)

def process_text_with_markup(full_text, default_voice):
    """
    Parses text for [voice:voice_id] tags.
    Splits by newlines to handle paragraph-level switching.
    """
    lines = full_text.split('\n')
    combined_audio = AudioSegment.empty()
    
    # Regex to find markup: [voice:af_bella]
    # Note: Using the raw ID (e.g., af_bella), not the friendly name
    markup_pattern = re.compile(r'^\[voice:([a-zA-Z0-9_]+)\]\s*(.*)')
    
    current_voice = default_voice
    
    # Reverse lookup map for validation
    valid_ids = list(VOICES.values())

    for line in lines:
        line = line.strip()
        if not line:
            continue # Skip empty lines

        match = markup_pattern.match(line)
        text_to_render = line

        if match:
            requested_voice = match.group(1)
            text_content = match.group(2)
            
            # Update voice if valid
            if requested_voice in valid_ids:
                current_voice = requested_voice
            
            text_to_render = text_content

        if text_to_render:
            segment = generate_audio_segment(text_to_render, current_voice)
            if segment:
                combined_audio += segment
                # Add a small pause between paragraphs
                combined_audio += AudioSegment.silent(duration=300) 

    return combined_audio