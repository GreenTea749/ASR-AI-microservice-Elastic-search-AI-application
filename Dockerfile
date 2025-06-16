# Dockerfile

FROM python:3.9-slim

# 1) System libs for audio I/O
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# 2) Working dir
WORKDIR /app

# 3) Copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Pre-download the wav2vec2 model into Hugging Face cache
RUN python - <<'EOF'
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC


Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
EOF

# 5) Copy only your ASR code
COPY asr/ ./asr

# 6) Expose port + launch
EXPOSE 8001
CMD ["uvicorn", "asr.asr_api:app", "--host", "0.0.0.0", "--port", "8001"]
