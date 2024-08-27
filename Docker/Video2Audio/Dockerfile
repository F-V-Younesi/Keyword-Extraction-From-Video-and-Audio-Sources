FROM ubuntu:24.04
RUN apt-get update
RUN apt-get install python3.10 python3-pip -y
COPY requirements.txt .
COPY sampleAudio.mp3 . 
COPY Video2Audio.py .
COPY video.mp4 .
RUN pip3 install -r requirements.txt --break-system-packages
CMD ["python3","Video2Audio.py"]