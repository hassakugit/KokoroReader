from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import pypdf
from typing import Optional

from app.audio_client import process_text_and_generate
from app.voice_data import get_formatted_voice_list
from app.history import add_entry, load_history

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "voices": get_formatted_voice_list(),
        "history": load_history()
    })

@app.post("/generate")
async def generate_tts(
    request: Request,
    text_input: Optional[str] = Form(None),
    voice_select: str = Form(...),
    voice_mix: Optional[str] = Form(None),
    speed: float = Form(1.0),
    api_url: str = Form(...),
    file_upload: Optional[UploadFile] = File(None)
):
    final_text = ""
    
    # 1. Parse Input
    if file_upload and file_upload.filename:
        temp_filename = f"temp_{uuid.uuid4()}_{file_upload.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file_upload.file, buffer)
        try:
            if file_upload.filename.lower().endswith('.pdf'):
                reader = pypdf.PdfReader(temp_filename)
                extracted = [page.extract_text() for page in reader.pages]
                final_text = "\n".join(extracted)
            else:
                with open(temp_filename, "r", encoding="utf-8") as f:
                    final_text = f.read()
        except Exception as e:
            return JSONResponse({"error": f"File Parse Error: {str(e)}"}, status_code=500)
        finally:
            if os.path.exists(temp_filename): os.remove(temp_filename)
    else:
        final_text = text_input or ""

    if not final_text.strip():
        return JSONResponse({"error": "No text provided"}, status_code=400)

    # 2. Process
    try:
        audio_segment = process_text_and_generate(
            final_text, 
            voice_select, 
            speed, 
            voice_mix, 
            api_url
        )
        
        if len(audio_segment) == 0:
            return JSONResponse({"error": "No audio generated"}, status_code=500)

        # 3. Save
        filename = f"speech_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join("app/static/audio", filename)
        audio_segment.export(output_path, format="wav")
        
        # 4. History
        # Format "Bella + Sarah" for display if mixed
        display_voice = voice_select
        if voice_mix and voice_mix != "none":
            display_voice += f" + {voice_mix}"
            
        updated_history = add_entry(filename, final_text, display_voice)
        
        return JSONResponse({
            "success": True, 
            "audio_url": f"/static/audio/{filename}",
            "history": updated_history
        })
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)