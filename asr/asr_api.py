import os
import tempfile
import librosa #to read audio files and resample them to 16kHz
from fastapi import FastAPI, File, UploadFile, HTTPException #using FASTAPI for hosting microservice and define web endpoint
from pydantic import BaseModel
from asr.wav2_models import transcribe_waveform
#Main API file for the ASR microservice

#create web application instance
app = FastAPI(title="HTX ASR Service", version="1.0")

#define the response model for the ASR endpoint
class TranscriptionResponse(BaseModel):
    transcription: str
    duration: str

#ping API for sanity check on the service
@app.get("/ping")
async def ping():
    return "pong"

#ASR endpoint
#when a POST request is made to the /asr endpoint, the asr function is called
@app.post("/asr", response_model=TranscriptionResponse)

#input: multipart/form-data with 'file' field containing the audio file
#output: application/json: {transcription: str, duration: str}
async def asr(file: UploadFile = File(...)) -> TranscriptionResponse:
    #save it to a temporary file
    suffix = os.path.splitext(file.filename)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(await file.read())
    tmp.close()
    try:
        #Load & resample to 16 kHz
        waveform, sr = librosa.load(tmp.name, sr=16_000)
        duration = len(waveform) / sr

        #Transcribe into text
        text = transcribe_waveform(waveform, sr)
    except Exception as e:
        #if any error occurs, raise an HTTP exception with status code 500
        raise HTTPException(status_code=500, detail=f"Error processing audio file: {str(e)}")
    finally:
        #remove the temporary file
        os.remove(tmp.name)

    #return the transcription and duration as a JSON response
    #need to manaually cast the duration to string type
    return TranscriptionResponse(transcription=text, duration=f"{duration:.1f}")

