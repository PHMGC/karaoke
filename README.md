# KaraokeTube
This project is a prototype of a website that generates a karaoke version of a YouTube video by removing the background audio and automatically adding subtitles. It uses Demucs to separate the voices from the background sound and Whisper to transcribe the subtitles.

It uses Flask for the backend application, SQL-Alchemy for its database, and React for the website frontend.

**Made by Gustavo Luiz and Pedro Cortez.**

# Usage
First, clone the repository
```bash
git clone https://github.com/PHMGC/karaoke.git
```
# Frontend

# Backend

First, enter the backend directory.
```bash
cd backend
```

## Requirements

* Python 3.8 or greater (if not installed, you can download it here: https://www.python.org/downloads)

* Ffmpeg (if not installed, you can download it here: https://www.ffmpeg.org/download.html)


* All dependencies from this project can be installed running:
```bash
pip install -r requirements.txt
```
* If you prefer to install them locally, you can create a python virtual enviroment:
```bash
python -m venv venv
```
To start the venv

> On Windows:
```bash
.\venv\Scripts\activate
```
> On Linux/macOS:
```bash
source venv/bin/activate
```

Then run:
```bash
pip install -r requirements.txt
```
to install the dependencies.

* Environment with CUDA support is recommended for better performance (optional).
To install it, run:
```bash
python cuda.py
```
This code will try to automatically install the latest PyTorch compatible with your CUDA version.

## Run Backend
```bash
python main.py
```
This command will start the backend, and will wait for request sent from the frontend.

When requested, demucs, whisper and ffmepg will process the data and return the finnshed video.

## Exit
If you want to close the backend application, type on console:
```bash
CTRL + C
```
If you chose to use the virtual enviroment, you can exit with:
```bash
deactivate
```

## Debugging
* If you want to test if the video processing is working, you can run
```bash
python debugging.py processtest
```
Or to test a certain url
```bash
python debugging.py processtest <url>
```
* If you want to update the database, run:
```bash
python debugging.py updatedb
```

## Project Structure
* process.py: Audio and subtitle processing, including audio extraction and transcription.
* main.py: Runs the backend's app.
* config.py: Contains the project settings.
* debugging.py: Tools for debugging and tuning during development.
## Technologies
* Demucs: To separate vocals and background music.
* Whisper: For automatic subtitle generation.
* PyTubeFix: For YouTube video access.
* FFmpeg: For manipulating audio and video files.
