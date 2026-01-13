from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import pypdf
from typing import Optional

from app.engine import get_voice_list, process_text_with_markup, VOICES, initialize_model
from app.history import add_entry, load_history

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def startup_event():
    """Trigger model download and initialization on startup"""
    print("--- STARTUP: Loading Models ---")
    initialize_model()
    print("--- STARTUP: Complete ---")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "voices": get_voice_list(),
        "history": load_history()
    })

@app.post("/generate")
async def generate_tts(
    request: Request,
    text_input: Optional[str] = Form(None),
    voice_select: str = Form(...),
    file_upload: Optional[UploadFile] = File(None)
):
    print(f"Received request: Voice={voice_select}, File={file_upload.filename if file_upload else 'None'}")
    
    final_text = ""
    
    # 1. Handle Text Source
    if file_upload and file_upload.filename:
        temp_filename = f"temp_{uuid.uuid4()}_{file_upload.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file_upload.file, buffer)
            
        try:
            if file_upload.filename.lower().endswith('.pdf'):
                print("Parsing PDF...")
                reader = pypdf.PdfReader(temp_filename)
                extracted_text = []
                for page in reader.pages:
                    extracted_text.append(page.extract_text())
                final_text = "\n".join(extracted_text)
            else:
                with open(temp_filename, "r", encoding="utf-8") as f:
                    final_text = f.read()
        except Exception as e:
            print(f"File parsing error: {e}")
            return JSONResponse({"error": f"Failed to parse file: {str(e)}"}, status_code=500)
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    else:
        final_text = text_input or ""

    if not final_text.strip():
        return JSONResponse({"error": "No text provided"}, status_code=400)

    # 2. Process TTS
    try:
        voice_id = VOICES.get(voice_select, voice_select)
        
        print(f"Generating audio for {len(final_text)} chars...")
        audio_segment = process_text_with_markup(final_text, voice_id)
        
        if len(audio_segment) == 0:
             return JSONResponse({"error": "Audio generation produced empty result"}, status_code=500)

        filename = f"speech_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join("app/static/audio", filename)
        
        audio_segment.export(output_path, format="wav")
        print(f"Saved to {output_path}")
        
        updated_history = add_entry(filename, final_text, voice_select)
        
        return JSONResponse({
            "success": True, 
            "audio_url": f"/static/audio/{filename}",
            "history": updated_history
        })
        
    except Exception as e:
        print(f"Generation Error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)