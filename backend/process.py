import os, shutil
import re
import time
import requests
import subprocess
from pytubefix import YouTube
from faster_whisper import WhisperModel
import torch

data_folder = "data"


def format_time(seconds):
    # Format time in seconds to SRT time format (HH:MM:SS,mmm)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


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
        return

    yt = YouTube(url)
    stream_video = yt.streams.get_highest_resolution()
    stream_video.download(output_path=video_path, filename="video.mp4")
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(output_path=video_path, filename="audio.mp3")

    thumbs_options = [
        "maxresdefault.jpg",
        "sddefault.jpg",
        "hqdefault.jpg",
        "mqdefault.jpg",
        "default.jpg",
    ]

    for option in thumbs_options:
        response = requests.get(f"https://img.youtube.com/vi/{uid}/" + option)
        if response.status_code == 200:
            with open(os.path.join(video_path, "thumbnail.jpg"), "wb") as f:
                f.write(response.content)
            return
    raise ConnectionError


def demucs_transcript(uid):
    # Load audio file
    audio_folder = os.path.join(data_folder, uid)
    if os.path.exists(os.path.join(audio_folder, "vocals.wav")) or os.path.exists(
        os.path.join(audio_folder, "no_vocals.wav")
    ):
        return
    print("demucs started")
    start = time.time()
    subprocess.run(
        [
            "demucs",
            os.path.join(audio_folder, "audio.mp3"),
            "--two-stems",
            "vocals",
            "--out",
            audio_folder,
        ]
    )
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


def whisper_transcript(uid):
    audio_folder = os.path.join(data_folder, uid)
    if os.path.exists(os.path.join(audio_folder, "vocals.srt")):
        pass  # return

    audio_path = os.path.join(audio_folder, "vocals.wav")

    print("whisper started")
    start = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("using", device)

    model = WhisperModel("large-v3", device=device)
    # language_info = model.detect_language_multi_segment(audio_path)
    segments, _ = model.transcribe(audio_path, beam_size=5, language=None)
    # print(
    #     "Detected language '%s' with probability %f"
    #     % (language_info["language_code"], language_info["language_confidence"])
    # )

    with open(os.path.join(audio_folder, "vocals.srt"), "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments):
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            # Write the index
            f.write(f"{i + 1}\n")

            # Format and write the timecodes
            start_time = format_time(segment.start)
            end_time = format_time(segment.end)
            f.write(f"{start_time} --> {end_time}\n")

            # Write the text
            f.write(f"{segment.text}\n\n")

    finnish = time.time()
    print(f"whisper finnished (took {format_time(finnish - start)})")


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


def cleanup(uid):
    no_delete = []
