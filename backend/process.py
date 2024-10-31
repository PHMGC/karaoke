import os, shutil, re, time, subprocess
import requests
from pytubefix import YouTube
import torch
from faster_whisper import WhisperModel

from models import VideoInfo

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
        thumbs_options = [
            "maxresdefault.jpg",
            "sddefault.jpg",
            "hqdefault.jpg",
            "mqdefault.jpg",
            "default.jpg",
        ]

        thumbnail = ""
        for option in thumbs_options:
            response = requests.get(f"https://img.youtube.com/vi/{uid}/" + option)
            if response.status_code == 200:
                thumbnail = f"https://img.youtube.com/vi/{uid}/maxresdefault.jpg"
                break

        vd = YouTube(url)
        title = vd.title
        channel = vd.author
        h, m, s = vd.length // 3600, (vd.length % 3600) // 60, vd.length % 60
        duration = f"{h}:{m:02}:{s:02}" if h else (f"{m}:{s:02}" if m else f"{s}s")
        return {
            "uid": uid,
            "title": title,
            "thumbnail": thumbnail,
            "channel": channel,
            "duration": duration,
        }

    except Exception as e:
        raise e("Error getting video id!")


def get_video(url, debug=False):
    print("get_video() started")
    start = time.time()
    
    uid = extract_uid(url)

    video_path = os.path.join(data_folder, uid)
    if not os.path.exists(video_path):
        os.makedirs(video_path)

    try:
        vd = YouTube(url)
        if debug:
            stream_video = vd.streams.get_highest_resolution()
            stream_video.download(output_path=video_path, filename="video.mp4")

        stream = vd.streams.filter(only_audio=True).first()
        stream.download(output_path=video_path, filename="audio.mp3")
    except Exception as e:
        raise e("Error getting video info")

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

            finnish = time.time()
            print(f"get_video() was successfull! (took {format_time(finnish - start)})")
        
    raise ConnectionError("Error downloading thumbnail!")


def demucs_transcript(uid):
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

        shutil.move(os.path.join(demucs_folder, "audio", "vocals.wav"), audio_folder)
        shutil.move(os.path.join(demucs_folder, "audio", "no_vocals.wav"), audio_folder)
        shutil.rmtree(demucs_folder)
    else:
        raise SystemError("demucs failed!")
    
    finnish = time.time()
    print(f"demucs_transcript() was successfull! (took {format_time(finnish - start)})")


def whisper_transcript(uid, queue=None):
    print("whisper_transcript() started!")
    start = time.time()

    audio_folder = os.path.join(data_folder, uid)

    audio_path = os.path.join(audio_folder, "vocals.wav")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("using", device)

    model = WhisperModel("large-v3", device=device)
    language_info = model.detect_language_multi_segment(audio_path)
    segments, _ = model.transcribe(
        audio_path, beam_size=5, language=language_info["language_code"]
    )
    print(
        "Detected language '%s' with probability %f"
        % (language_info["language_code"], language_info["language_confidence"])
    )

    with open(os.path.join(audio_folder, "vocals.srt"), "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments):
            progress = i/len(segments) * 100
            if queue is not None:
                queue.put(progress)
            print(f"Progress: {progress}%")
            # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            # Write the index
            f.write(f"{i + 1}\n")

            # Format and write the timecodes
            start_time = format_time(segment.start)
            end_time = format_time(segment.end)
            f.write(f"{start_time} --> {end_time}\n")

            # Write the text
            f.write(f"{segment.text}\n\n")

    if not os.path.exists(os.path.join(audio_folder, "vocals.srt")):
        raise SystemError("whisper failed!")

    finnish = time.time()
    print(f"whisper_transcript() was successfull! (took {format_time(finnish - start)})")


def generate_video(uid, debug=False):
    print("generate_video() started!")
    start = time.time()

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
            "subtitles=vocals.srt",  # Insere a legenda no vídeo
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
    if debug:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                "video.mp4",
                "-vf",
                "subtitles=vocals.srt",  # Insere a legenda no vídeo
                "-y",
                "sub_video.mp4",
            ],
            cwd=folder_path,
        )

    if not os.path.exists(os.path.join(data_folder, uid, "final_video.mp4")):
        raise SystemError("ffmpeg failed!")

    finnish = time.time()
    print(f"generate_video() was successfull! (took {format_time(finnish - start)})")


def cleanup(uid):
    no_delete = []
