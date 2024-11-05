# KaraokeTube
This project is a prototype of a website that generates a karaoke version of a YouTube video by removing the background audio and automatically adding subtitles. It uses Demucs to separate the voices from the background sound and Whisper to transcribe the subtitles.

It uses Flask for the backend application, and React for the website frontend.

Made by Gustavo Luiz (Frontend) and Pedro Cortez(Backend)

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
* Environment with CUDA support is recommended for better performance (optional).

This repository contains an python venv, with all dependencies already installed.
However, if you prefer, you can install all other dependencies on your machine using the command below:
```bash
python pip install --force-reinstall -r requirements.txt
```

## Configuration

If you are using the virtual enviroment:
On Windows:
```bash
.\venv\Scripts\activate
```
On Linux/macOS:
```bash
source venv/bin/activate
```
## Run Backend
```bash
python main.py
```
This command will start the backend, and will wait for request sent from the frontend.

When requested, demucs, whisper and ffmepg will process the data and return the finnshed video

## Exit
If you want to close the backend application, type on console:
```bash
CTRL + C
```
And, if you are using venv, type on console:
```bash
deactivate
```
To close the virtual environment.

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
