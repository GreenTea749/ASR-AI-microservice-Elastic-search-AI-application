import os
import tempfile
import librosa #to read audio files and resample them to 16kHz

from fastapi import FastAPI, File, UploadFile, HTTPException # to define web endpoints
from pydantic import BaseModel
from .wav2_models import transcribe_waveform # to transcribe audio files into text using the ASR ai model

#create web application instance
app = FastAPI(title="HTX ASR Service", version="1.0")

#define the response model for the ASR endpoint
class TranscriptionResponse(BaseModel):
    transcription: str
    duration: str

#ping API for sanity check on the service
@app.get("/ping")
async def ping():
    return {"message": "pong"}

#ASR endpoint
@app.post("/asr", response_model=TranscriptionResponse)
#when a POST request is made to the /asr endpoint, the asr function is called

#input parameter: content-type: multipart/form-data: file[string type] (binary of an audio mp3 file)
#output: content-type: application/json: {transcription: string type, duration: string type}
async def asr(file: UploadFile = File(...)):
    #check if the file is an audio file
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files accepted")

    #save it to a temporary file
    suffix = os.path.splitext(file.filename)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(await file.read())
    tmp.close()

    try:
        #Load & resample to 16 kHz
        waveform, sr = librosa.load(tmp.name, sr=16_000)
        duration = len(waveform) / sr

        # Transcribe into text
        text = transcribe_waveform(waveform, sr)
    finally:
        #remove the temporary file
        os.remove(tmp.name)

    #return the transcription and duration as a JSON response
    #need to manaually cast the duration to string type
    return TranscriptionResponse(transcription=text, duration=f"{duration:.1f}")

