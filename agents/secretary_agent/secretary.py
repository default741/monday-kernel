import os
import whisper
import requests
from fastapi import FastAPI, UploadFile, File, BackgroundTasks

app = FastAPI(title="Monday Kernel: Secretary Agent")

# Load the model once when the server starts
# 'base' is a good balance of speed and accuracy
model = whisper.load_model("base")

VAULT_URL = "http://localhost:3000/proxy/ingest"

def transcribe_and_vault(file_path: str):
    print(f"👂 Secretary is listening to: {file_path}")

    # 1. Transcribe the audio
    result = model.transcribe(file_path)
    text = result["text"]

    # 2. Prepare the payload for the Vault (via Rust)
    payload = {
        "content": f"VOICE MEMO: {text}",
        "category": "Voice Note",
        "tags": ["audio", "whisper", "automated"]
    }

    # 3. Send to Vault
    try:
        response = requests.post(VAULT_URL, json=payload)
        print(f"✅ Successfully vaulted audio context: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to vault audio: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/upload-audio")
async def upload_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        buffer.write(await file.read())

    # Run transcription in the background so the API stays responsive
    background_tasks.add_task(transcribe_and_vault, temp_filename)

    return {"message": "Audio received! Secretary is processing it in the background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)