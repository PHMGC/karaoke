import os, shutil
import re
import time
import requests
import subprocess
from pytubefix import YouTube

from config import db
from models import VideoInfo
import torch

data_folder = "data"


def extract_uid(url):
    # Regular expression to match YouTube video IDs
    pattern = r"(?:v=|\/|youtu\.be\/|\/embed\/|\/v\/|\/watch\?v=|\/\?v=|&v=|\/shorts\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return None


def get_video_info(url):
    uid = extract_uid(url)
    if uid is None:
        return None
    try:
        thumbnail = f"https://img.youtube.com/vi/{uid}/maxresdefault.jpg"
        yt = YouTube(url)
        title = yt.title
        channel = yt.author
        h, m, s = yt.length // 3600, (yt.length % 3600) // 60, yt.length % 60
        duration = f"{h}:{m:02}:{s:02}" if h else (f"{m}:{s:02}" if m else f"{s}")
        return {
            "title": title,
            "thumbnail": thumbnail,
            "channel": channel,
            "duration": duration,
        }

    except Exception:
        return None


def get_video(url):
    uid = extract_uid(url)
    if uid is None:
        raise ValueError

    video_path = os.path.join(data_folder, uid)
    if not os.path.exists(video_path):
        os.makedirs(video_path)
    else:
        pass  # return

    response = requests.get(f"https://img.youtube.com/vi/{uid}/maxresdefault.jpg")
    if response.status_code == 200:
        with open(os.path.join(video_path, "thumbnail.jpg"), "wb") as f:
            f.write(response.content)
    else:
        raise ConnectionError

    yt = YouTube(url)
    stream_video = yt.streams.get_highest_resolution()
    stream_video.download(output_path=video_path, filename="video.mp4")
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(output_path=video_path, filename="audio.mp3")

    # title = yt.title
    # channel = yt.author
    # h, m, s = yt.length // 3600, (yt.length % 3600) // 60, yt.length % 60
    # duration = f"{h}:{m:02}:{s:02}" if h else (f"{m}:{s:02}" if m else f"{s}")

    # video_info = VideoInfo(uid=uid, title=title, channel=channel, duration=duration)

    # try:
    #     db.session.add(video_info)
    #     db.session.commit()
    # except Exception as e:
    #     raise e


def get_progress_output(console):
    if console.poll() is not None or console is None or console.stderr is None:
        return 100
    print("saida", console.stdout.readline())
    print("erro", console.stderr.readline())
    return 0
    # result = "".join(re.findall(r"\d+", console.stderr.readline()[:5]))
    # return 0 if len(result) == 0 or not result.isnumeric() else int(result)


def demucs_transcript(uid):
    # Load audio file
    audio_folder = os.path.join(data_folder, uid)
    if os.path.exists(os.path.join(audio_folder, "vocals.wav")) or os.path.exists(
        os.path.join(audio_folder, "no_vocals.wav")
    ):
        pass  # return
    print("demucs started")
    start = time.time()
    console = subprocess.Popen(
        [
            "demucs",
            os.path.join(audio_folder, "audio.mp3"),
            "--two-stems",
            "vocals",
            "--out",
            audio_folder,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    progress = 0
    while console.poll() is None:
        progress = get_progress_output(console)
        print("demucs:", progress)
    finnish = time.time()
    print(f"demucs finnished (took {format_time(finnish - start)})")

    demucs_folder = os.path.join(audio_folder, "htdemucs")
    if os.path.exists(demucs_folder):
        vocals = os.path.join(audio_folder, "vocals.wav")
        no_vocals = os.path.join(audio_folder, "no_vocals.wav")

        if os.path.exists(vocals):
            os.remove(vocals)
        if os.path.exists(no_vocals):
            os.remove(no_vocals)

        shutil.move(os.path.join(demucs_folder, "audio", "vocals.wav"), audio_folder)
        shutil.move(os.path.join(demucs_folder, "audio", "no_vocals.wav"), audio_folder)
        shutil.rmtree(demucs_folder)
    else:
        raise SystemError


def format_time(seconds):
    # Format time in seconds to SRT time format (HH:MM:SS,mmm)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def whisper_transcript(uid):
    audio_folder = os.path.join(data_folder, uid)
    if os.path.exists(os.path.join(audio_folder, "vocals.srt")):
        pass  # return

    audio_path = os.path.join(audio_folder, "vocals.wav")

    print("whisper started")
    start = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("using", device)
    # subtitles = model.transcribe(audio_path, verbose=False)
    console = subprocess.Popen(
        [
            "whisper",
            audio_path,
            "--model",
            "medium",
            "--device",
            device,
            "--verbose",
            "False",
            "--output_dir",
            audio_folder,
            "--output_format",
            "srt",
            "-y",
        ]
    )
    progress = 0
    while console.poll() is None:
        progress = get_progress_output(console)
        print("whisper:", progress)
        time.sleep(1)
    console.wait()
    finnish = time.time()
    print(f"whisper finnished (took {format_time(finnish - start)})")

    # with open(os.path.join(audio_folder, "vocals.srt"), "w", encoding="utf-8") as f:
    #     for segment in subtitles["segments"]:
    #         # Write the index
    #         f.write(f"{segment["id"] + 1}\n")

    #         # Format and write the timecodes
    #         start_time = format_time(segment["start"])
    #         end_time = format_time(segment["end"])
    #         f.write(f"{start_time} --> {end_time}\n")

    #         # Write the text
    #         f.write(f"{segment['text']}\n\n")

    print(".srt saved")


def generate_video(uid):
    folder_path = os.path.join(data_folder, uid)
    subprocess.run(
        [
            "ffmpeg",
            "-loop",
            "1",  # Repete a imagem
            "-i",
            "thumbnail.jpg",  # Imagem de entrada
            "-i",
            "no_vocals.wav",  # Áudio de entrada
            "-vf",
            "gblur=sigma=20",  # Aplica desfoque gaussiano na imagem
            "-vf",
            "subtitles=subtitles.srt",  # Insere a legenda no vídeo
            "-c:v",
            "libx264",  # Codec de vídeo
            "-tune",
            "stillimage",  # Ajuste para imagens estáticas
            "-c:a",
            "aac",  # Codec de áudio
            "-b:a",
            "192k",  # Taxa de bits do áudio
            "-pix_fmt",
            "yuv420p",  # Formato de pixel
            "-shortest",  # Faz com que o vídeo tenha a duração do áudio
            "-y",
            "final_video.mp4",
        ],
        cwd=folder_path,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            "video.mp4",
            "-vf",
            "subtitles=subtitles.srt",  # Insere a legenda no vídeo
            "-y",
            "sub_video.mp4",
        ],
        cwd=folder_path,
    )
