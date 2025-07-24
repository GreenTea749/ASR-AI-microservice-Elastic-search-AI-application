This repository contains 2 project tasks that showcases deployment of practical AI tools and infrasctructure.

The first project task is a fully containerized Automatic Speech Recognition (ASR) microservice using FastAPI and Facebook’s Wav2Vec2 model from Hugging Face, capable of transcribing thousands of audio files with low latency. This project task showcases how to integrate a deep learning model intoa web service, process audio input, and deploy the service using Docker.

The second project task is the deployment of a full-stack search engine that indexes the transcriptions made from the previous task, and enables intelligent querying through a user-friendly frontend built with React and Elasticsearch. The search engine are deployed via Docker and hosted on an AWS EC2 instance, demonstrating scalable, end-to-end deployment of real-world ML pipelines.


# Task 1 – Automatic Speech Recognition (ASR) Microservice  
**Created by Cleon**
For task 1, I have created and hosted microservice that delivers a FastAPI-based ASR model for transcribing audio files with low latency and high throughput. It’s fully containerized for seamless local or cloud deployment.

---

## Deployment Architecture

- **FastAPI ASR Service**: Hosts the speech recognition model and exposes a `/asr` endpoint.  
- **Uvicorn Worker**: Serves the FastAPI app with automatic reload for development.  
- **Dataset**: `cv-valid-dev` directory containing Common Voice audio and metadata CSV.  
- **Index**: Outputs appended to `generated_text` column in `cv-valid-dev.csv` for downstream analysis.
---

## Quick Start (Local)
The bash code provided in this section caters is meant for local environment. The dependencies can be found in the requirements.txt file. This bash code is used by myself to mass transcribe audio files into the excel file cv-valid-dev/cv-valid-dev.csv.
### Backend Setup
```bash
uvicorn asr.asr_api:app --host 0.0.0.0 --port 8001 --reload
```

should see: Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)

testing: we can check if the service is working by running a ping test
type this command on another shell:
```bash
curl http://localhost:8001/ping
```

should see this

Content           : {"pong"}

This means that the service is working and ready to transcribe your audio files.

### To transcribe a audio file using this service, type in the command below, replacing it with the path of the desired audio file
example: using 'cv-valid-dev/sample-000000.mp3' file
```bash
curl -F "file=@cv-valid-dev/sample-000000.mp3"      http://localhost:8001/asr
```
> Returns JSON:
> ```json
> { "text": "Your transcribed text here" }
> ```

---

### Bulk Transcription
To test the capabilities of this service, 4076 common-voice files (under the 'common_voice/cv-valid-dev' folder) has be transcribed using the asr end point. The transcribed text has been saved back into a new column: 'generated_text' in the cv-valid-dev.csv

The following command is used to run the test

```bash
python asr/cv-decode.py
```
- Reads each `.mp3` in `cv-valid-dev/`  
- Calls `/asr` endpoint  
- Writes `generated_text` column in `cv-valid-dev.csv`
---

The bash code in this section can be used to containerise the microservice and perform the same functions as the local deployment in the previous section.
## Containerization

### Build Docker Image
```bash
docker build -t asr-api .
```

### Run as Container
```bash
docker run -d --name asr-api \
  -p 8001:8001 \
  -v "$PWD/cv-valid-dev:/app/cv-valid-dev" \
  asr-api
```

### To test the service inside the container:
```bash
curl http://localhost:8001/ping
curl -F "file=@cv-valid-dev/sample-000000.mp3" http://localhost:8001/asr
```

### To stop and clean up:
```bash
docker stop asr-api
docker rm asr-api
```

## if you would like to conduct the large scale transcription testing using the containerize version, it is needed to mount the 'cv-valid-dev' data folder at runtime first. Ensure that the previous docker image is removed first

```bash
docker run --rm \
  --network host \
  -v "$PWD/cv-valid-dev:/app/cv-valid-dev" \
  -w /app/asr \
  asr-api \
  python cv-decode.py
  ```

# Task 2 – Full-Stack Search Engine for Audio Transcriptions  
**Created by Cleon**

For the next task, I have deployed a search engine to allow end users to perform intelligent queries on a CSV file dataset. As this project is for learning purposes and a proof of concept (POC), the CSV file used is the cv-valid-dev.csv found in the previous task.
This deployment consists of using Elasticsearch as the backend, wired to a Search UI frontend web application. It is containerized and hosted on AWS EC2, which can be accessed via the following link: 
- A 2-node Elasticsearch cluster (via Docker)  
- A React frontend using Elastic Search-UI  
- Full containerization for local or AWS EC2 free-tier deployment

---

## Deployment Architecture

See architecture diagram: [`deployment-design/design.pdf`](deployment-design/design.pdf)

Key components:
- `es01` and `es02`: Two-node Elasticsearch cluster (1 primary shard, 0 replicas)
- `search-ui`: React frontend for end-user querying
- `esnet`: User-defined Docker bridge network
- Index name: `cv-transcriptions`


website link: http://13.212.113.101:3000/
---

## Quick Start (Local)

### Backend Setup

```bash
cd elastic-backend
docker compose down -v
docker network create esnet 2>/dev/null || true
docker compose up -d --build
```

Verify cluster health:

```bash
curl http://localhost:9200/_cluster/health?pretty
curl http://localhost:9200/cv-transcriptions/_count?pretty
```

Optional test query:

```bash
curl -X GET "http://localhost:9200/cv-transcriptions/_search?pretty" \
     -H 'Content-Type: application/json' \
     -d'{ "query": { "match": { "gender": "female" } } }'
```

---

### Frontend Setup

```bash
cd ../search-ui
docker compose down
docker compose build --no-cache ui
docker compose up -d ui
```

Then visit: [http://localhost:3000](http://localhost:3000)

---

## Cleaning Up

```bash
# Backend cleanup
cd ../elastic-backend
docker compose down -v

# Frontend cleanup
cd ../search-ui
rm -rf search-ui
```

To re-import dataset later:

```bash
cd elastic-backend
docker compose run --rm indexer
```

---

## Public Deployment

This app is deployable on any public VM (e.g., AWS EC2, Azure B1s) using Docker and a public IP. No managed services are used.

**Live Demo**: http://13.212.113.101:3000/
(not available at this moment)
---

## Searchable Fields

The following fields are indexed and searchable:

- `generated_text`
- `duration`
- `age`
- `gender`
- `accent`
