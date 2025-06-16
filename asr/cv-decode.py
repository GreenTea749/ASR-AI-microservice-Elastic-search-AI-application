import os
import sys
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm

#call API to transcribe common-voice mp3 files under the cv-valid-dev folder

#steps:
#read cv-valid-dev.csv
#for each row, locate corresponding mp3 file in the cv-valid-dev folder
#post it into /asr endpoint
#collect the transcription and duration
#save it into the same csv file as a new column 'generated_text'
#save the csv

#URL of local ASR service
API_URL = "http://localhost:8001/asr"

#Path to the folder containing the MP3s and the CSV
DATA_DIR = Path(__file__).parent.parent / "cv-valid-dev"
CSV_PATH = DATA_DIR / "cv-valid-dev.csv"
print(f"Using data directory: {DATA_DIR}")
print(f"Using CSV file: {CSV_PATH}")

#send 1 file into /asr endpoint and get the transcription
#input: mp3_path: Path object of the mp3 file
#output: transcription: string type
#raises on non-200 responses
def transcribe_file(mp3_path: Path) -> str:
    with mp3_path.open("rb") as f:
        files = {"file": (mp3_path.name, f, "audio/mpeg")}
        resp = requests.post(API_URL, files=files)
        resp.raise_for_status()
        data = resp.json()
        # data == {"transcription": "...", "duration": "..."}
        return data["transcription"]

def main():
    #load csv
    df = pd.read_csv(CSV_PATH)
    #check for column 'path', which points to MP3 filename.
    if "filename" not in df.columns:
        print("ERROR: 'filename' column not found in CSV", file=sys.stderr)
        sys.exit(1)

    #Interate over each row in the CSV file and transcribe the audio files
    generated = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Transcribing"):
        filename = Path(row["filename"]).name
        mp3_path = DATA_DIR / filename
        if not mp3_path.exists():
            print("WARNING: missing file", mp3_path, file=sys.stderr)
            generated.append("")
            continue
        try:
            text = transcribe_file(mp3_path)
        except Exception as e:
            print(f"Error: transcribing {mp3_path}: {e}", file=sys.stderr)
            text = ""
        print(f" transcribed text: {text}")
        generated.append(text)

    #Attach the generated text to the 'generated_text' column in the CSV file
    df["generated_text"] = generated
    df.to_csv(CSV_PATH, index=False)
    print(f"Updated CSV with generated_text is written to {CSV_PATH}")

if __name__ == "__main__":
    main()


