import os
import torch
import numpy as np
import soundfile as sf
from kokoro import KPipeline
from pydub import AudioSegment
import io
import re
import sys

# Global pipeline variable
PIPELINE = None
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Map of friendly names to voice codes
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

def initialize_model():
    """
    Initializes the Kokoro pipeline. 
    This triggers the download of the model weights (~300MB) if not cached.
    """
    global PIPELINE
    print(f"--> Initializing Kokoro Pipeline on device: {device}...")
    try:
        # Initialize pipeline (downloads weights if needed)
        PIPELINE = KPipeline(lang_code='a', device=device)
        
        # Warmup: Run a tiny generation to ensure espeak and model are loaded
        print("--> Running warmup generation...")
        dummy_gen = PIPELINE("Hello", voice="af_bella", speed=1)
        for _ in dummy_gen: 
            pass
        print("--> Model ready.")
    except Exception as e:
        print(f"!!! CRITICAL ERROR initializing model: {e}")
        # We re-raise so the container fails fast if the model is broken
        raise e

def get_voice_list():
    return VOICES

def generate_audio_segment(text, voice_key):
    global PIPELINE
    if PIPELINE is None:
        raise RuntimeError("Pipeline not initialized")
        
    if not text.strip():
        return None
    
    # Generate audio
    generator = PIPELINE(text, voice=voice_key, speed=1, split_pattern=r'\n+')
    
    all_audio = []
    for _, _, audio in generator:
        all_audio.append(audio)
        
    if not all_audio:
        return None

    final_audio_np = np.concatenate(all_audio)
    
    # Convert to WAV in memory
    buffer = io.BytesIO()
    sf.write(buffer, final_audio_np, 24000, format='WAV')
    buffer.seek(0)
    
    return AudioSegment.from_wav(buffer)

def process_text_with_markup(full_text, default_voice):
    lines = full_text.split('\n')
    combined_audio = AudioSegment.empty()
    
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
            if requested_voice in valid_ids:
                current_voice = requested_voice
            text_to_render = text_content

        if text_to_render:
            try:
                segment = generate_audio_segment(text_to_render, current_voice)
                if segment:
                    combined_audio += segment
                    combined_audio += AudioSegment.silent(duration=300) 
            except Exception as e:
                print(f"Error rendering segment '{text_to_render[:20]}...': {e}")

    return combined_audio