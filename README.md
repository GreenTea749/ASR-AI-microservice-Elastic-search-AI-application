# myrepo
Contains my HTX technical test question

# task: create a hosted microservice to deploy an automatic sppech recognition AI model that can be used to
# transcribe any audio files




# 1 testing: check if the service is working

to check, need run a ping test:

1) start the thing:
>> uvicorn asr.asr_api:app --host 0.0.0.0 --port 8001 --reload

should see: Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)

2) on another shell, type this:
>> curl http://localhost:8001/ping

should see minimumly this:

Content           : {"message":"pong"}

This mean that the service is working



3) transcribe 4076 common-voice files using the asr end point, and save them back into a new column: 'generated_text'

run ASR server
>> uvicorn asr.asr_api:app --reload

run decoder
>> python asr/cv-decode.py




4) Build the docker image (if its not built)
>> docker build -t asr-api .

5) run the container
>> docker run -d --name asr-api -p 8001:8001 asr-api

6) test if it is working
>>curl http://localhost:8001/ping

expected output:
>> {"message":"pong"}


7) 

#server: fastAPI application, running under uvicorn.

Wait and listen for HTTP requests on port (8001)

When clieent ask for something by hitting a url (get/ping or post/asr),
server does some work, then return the status code

get: retrive info without side-effects (fetch pong)
post: send data that cause server to do something (upload audio, tirgger transcription)


# qn 3

