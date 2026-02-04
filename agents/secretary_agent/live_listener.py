from fastapi import FastAPI, BackgroundTasks
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import os
import whisper

app = FastAPI()
model = whisper.load_model("base")
is_listening = False

def record_loop():
    global is_listening
    fs = 16000
    duration = 30

    while is_listening:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        wav.write("temp_live.wav", fs, recording)

        # Transcribe with CPU optimization
        result = model.transcribe("temp_live.wav", fp16=False)
        text = result["text"].strip()

        if len(text) > 10:
            requests.post("http://localhost:3000/proxy/ingest", json={
                "content": text,
                "category": "Meeting Note",
                "tags": ["live", "voice-command"]
            })

@app.post("/toggle")
async def toggle_listener(background_tasks: BackgroundTasks):
    global is_listening
    is_listening = not is_listening
    if is_listening:
        background_tasks.add_task(record_loop)
        return {"status": "started", "message": "🎙️ Secretary is now listening..."}
    else:
        return {"status": "stopped", "message": "📴 Secretary stopped."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) # New port for control