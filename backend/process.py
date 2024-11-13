import os
import shutil
import re
import time
import subprocess
import numpy as np
import pysrt
import requests
from pytubefix import YouTube
from youtubesearchpython import VideosSearch
import torch
from faster_whisper import WhisperModel
import librosa
from pathlib import Path

device = "cuda" if torch.cuda.is_available() else "cpu"
# device = "cpu"
print("Whisper is using", device)

# see models here: https://github.com/SYSTRAN/faster-whisper

# model = WhisperModel("distil-large-v2", device=device)
model = WhisperModel("large-v2", device=device)


def format_time(seconds):
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    return f"{h}:{m:02}:{s:.2f}" if h else (
        f"{m}:{s:.2f}" if m else f"{s:.2f}s")


def extract_uid(url):
    # Regular expression to match YouTube video IDs
    pattern = r"(?:v=|\/|youtu\.be\/|\/embed\/|\/v\/|\/watch\?v=|\/\?v=|&v=|\/shorts\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return None


def search_video_info(prompt, amount=1):
    try:
        search = VideosSearch(prompt, limit=amount)
        videos = search.result()['result']
        response = []
        for vd in videos:
            response.append({'uid': vd['id'],
                             'title': vd['title'],
                             'thumbnail': vd['thumbnails'][-1]['url'] if vd['thumbnails'] else None,
                             'channel': vd['channel']['name'],
                             'duration': vd.get('duration', 'N/A')
                             })
        return response[0] if len(response) == 1 else response
    except Exception as e:
        raise e("Error searching video from prompt!")


def get_video(url, data_folder):
    print("get_video() started")
    start = time.time()

    vd = YouTube(url)
    video_path = os.path.join(data_folder, vd.video_id)
    if not os.path.exists(video_path):
        os.makedirs(video_path)

    stream = vd.streams.filter(only_audio=True).first()
    stream.download(output_path=video_path, filename="audio.mp3")

    thumb = requests.get(vd.thumbnail_url)
    with open(os.path.join(video_path, "thumbnail.jpg"), "wb") as f:
        f.write(thumb.content)

    finnish = time.time()
    print(f"get_video() was successfull! (took {
        format_time(finnish - start)})")


def demucs_transcript(uid, data_folder):
    print("demucs_transcript() started")
    start = time.time()

    audio_folder = os.path.join(data_folder, uid)
    subprocess.run(
        [
            "demucs",
            os.path.join(audio_folder, "audio.mp3"),
            "--two-stems",
            "vocals",
            "--out",
            audio_folder,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    demucs_folder = os.path.join(audio_folder, "htdemucs")
    if os.path.exists(demucs_folder):
        vocals = os.path.join(audio_folder, "vocals.wav")
        no_vocals = os.path.join(audio_folder, "no_vocals.wav")

        if os.path.exists(vocals):
            os.remove(vocals)
        if os.path.exists(no_vocals):
            os.remove(no_vocals)
        shutil.move(os.path.join(demucs_folder, "audio",
                    "vocals.wav"), audio_folder)
        shutil.move(os.path.join(demucs_folder, "audio",
                    "no_vocals.wav"), audio_folder)
        shutil.rmtree(demucs_folder)
    else:
        raise SystemError("demucs failed!")

    finnish = time.time()
    print(f"demucs_transcript() was successfull! (took {
          format_time(finnish - start)})")


def first_no_silence(audio_path):
    audio, sr = librosa.load(audio_path, sr=44100)
    audio_db = librosa.amplitude_to_db(audio, ref=np.max)

    for i, db in enumerate(audio_db):
        if db > -50:
            return i/44100


def format_srt(subs_file):
    subs = pysrt.open(subs_file)
    for sub in subs:
        frases = re.findall(r'\b(?!I\s|I\'m\s)([A-Z][^A-Z]*)', sub.text)
        sub.text = '\n'.join(frase.strip() for frase in frases)
    subs.save()


def whisper_transcript(uid, data_folder, queue=None):
    print("whisper_transcript() started")
    start = time.time()

    audio_folder = os.path.join(data_folder, uid)
    audio_path = os.path.join(audio_folder, "vocals.wav")

    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        print(f"Audio file not found or empty: {audio_path}")
        return

    first_sub = first_no_silence(audio_path)

    language_info = model.detect_language_multi_segment(audio_path)
    language = language_info["language_code"]
    segments, info = model.transcribe(
        audio_path, beam_size=5, language=language
    )

    print(f"Detected language {language} with probability {
          language_info["language_confidence"]}")

    with open(os.path.join(audio_folder, "vocals.srt"), "w", encoding="utf-8") as f:
        total_duration = round(info.duration, 2)
        curr_duration = 0
        for i, segment in enumerate(segments):
            curr_duration += segment.end - segment.start
            progress = int((curr_duration / total_duration) * 100)
            if queue is not None:
                queue.put(progress)

            f.write(f"{i + 1}\n")
            if i == 0:
                start_time = format_time(first_sub)
            else:
                start_time = format_time(segment.start)
            end_time = format_time(segment.end)
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{segment.text}\n\n")

    subs_file = os.path.join(audio_folder, "vocals.srt")
    if not os.path.exists(subs_file):
        raise SystemError("whisper failed!")

    # formating the .srt, so the subs can be visibly better
    format_srt(subs_file)

    progress = 100
    if queue is not None:
        queue.put(progress)
    finnish = time.time()
    print(f"whisper_transcript() was successful! (took {
          format_time(finnish - start)})")


def generate_video(uid, data_folder, debug=False):
    print("generate_video() started")
    start = time.time()

    output_path = os.path.join(data_folder, uid)
    subprocess.run(
        [
            "ffmpeg",
            "-loop", "1",
            "-i", "thumbnail.jpg",
            "-i", "no_vocals.wav",
            "-vf", "gblur=sigma=20,subtitles=vocals.srt",
            "-shortest",
            "-y",
            "final_video.mp4",
        ],
        cwd=output_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if debug:
        subprocess.run(
            [
                "ffmpeg",
                "-loop", "1",
                "-i", "thumbnail.jpg",
                "-i", "audio.mp3",
                "-vf", "gblur=sigma=20,subtitles=vocals.srt",
                "-shortest",
                "-y",
                "final_video_debug.mp4",
            ],
            cwd=output_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    final_video_path = Path(output_path) / "final_video.mp4"
    if not final_video_path.exists():
        raise SystemError("ffmpeg failed!")

    finnish = time.time()
    print(f"generate_video() was successfull! (took {
          format_time(finnish - start)})")


def cleanup(uid, data_folder):
    print("cleanup started")
    no_delete = ["final_video.mp4", "final_video_debug.mp4"]
    video_folder = os.path.join(data_folder, uid)
    for file in os.listdir(video_folder):
        file_path = os.path.join(video_folder, file)
        if os.path.isfile(file_path) and file not in no_delete:
            os.remove(file_path)
    print("cleanup finnished")
