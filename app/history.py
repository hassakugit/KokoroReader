import json
import os
from datetime import datetime

HISTORY_FILE = "/app/data/history.json"
MAX_HISTORY = 25

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def add_entry(filename, text_snippet, voice):
    history = load_history()
    
    entry = {
        "filename": filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "snippet": text_snippet[:50] + "..." if len(text_snippet) > 50 else text_snippet,
        "voice": voice
    }
    
    # Prepend new entry
    history.insert(0, entry)
    
    # Keep only last 25
    if len(history) > MAX_HISTORY:
        # We could also delete the old file here to save space
        history = history[:MAX_HISTORY]
        
    save_history(history)
    return history