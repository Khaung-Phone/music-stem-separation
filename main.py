import os
import shutil
import torch
import torchaudio
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from demucs import pretrained
from demucs.apply import apply_model
from demucs.audio import convert_audio
from pathlib import Path

# Initialize FastAPI app
app = FastAPI()

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "separated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Serve static files from /separated/
app.mount("/separated", StaticFiles(directory=OUTPUT_DIR), name="separated")

# Load Demucs model
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"🔧 Using device: {device}")

model = pretrained.get_model("htdemucs")
model.to(device).eval()


def separate_audio(input_path: str):
    """Performs source separation on an input audio file using Demucs."""
    try:
        # Load audio file
        wav, sr = torchaudio.load(input_path)

        # Ensure stereo format
        wav = convert_audio(wav, sr, model.samplerate, model.audio_channels)
        wav = wav.to(device)[None, ...]

        # Apply Demucs model
        sources = apply_model(model, wav, device=device)
        sources = sources.squeeze(0).cpu()

        # Save separated sources
        stem_names = ["drums", "bass", "other", "vocals"]
        separated_files = {}

        for i, stem in enumerate(stem_names):
            output_path = os.path.join(OUTPUT_DIR, f"{stem}.wav")
            torchaudio.save(output_path, sources[i], model.samplerate, format="wav")
            
            # Return full URL to the client
            separated_files[stem] = f"http://localhost:8000/separated/{stem}.wav"

        return separated_files

    except Exception as e:
        return {"error": str(e)}


@app.post("/separate")
async def separate(file: UploadFile = File(...)):
    """API endpoint to upload an audio file and separate it into stems."""
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run separation
        separated_files = separate_audio(file_path)

        if "error" in separated_files:
            return JSONResponse(content=separated_files, status_code=500)

        return {"files": separated_files}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
