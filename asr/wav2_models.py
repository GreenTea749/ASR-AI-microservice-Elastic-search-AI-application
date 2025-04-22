#contains the wav2vec2 model for ASR
#This model is used to transcribe audio files into text

from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
 
# load model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
model.eval()  # set to evaluation mode
     
#load dummy dataset
ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation", trust_remote_code=True)

# check if it works
#input: audio file (format 1D float array) & sampling rate in Hz
#output: transcription in plain text
def transcribe_waveform(waveform: list[float], sampling_rate: int):
    #Tokenize
    inputs = processor(waveform, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    #Retrive logits
    with torch.no_grad():
        logits = model(**inputs).logits
    #Decode into text
    pred_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(pred_ids)[0]
    return transcription.lower()

__all__ = ["ds", "transcribe_waveform"]

