import re
from pytube import YouTube
from flask import request, jsonify

from config import app, db


def extract_video_id(url):
    # Regular expression to match YouTube video IDs
    pattern = r"(?:v=|\/|youtu\.be\/|\/embed\/|\/v\/|\/watch\?v=|\/\?v=|&v=|\/shorts\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return None


@app.route("/api/video/info", methods=["POST"])
def handle_url():
    url = request.json.get("url")
    video_id = extract_video_id(url)
    if video_id is None:
        return jsonify({"message": "Invalid url!"}), 400
    try:
        thumbnail = (
            f"https://img.youtube.com/vi/{extract_video_id(url)}/maxresdefault.jpg"
        )
        yt = YouTube(url)
        title = yt.title
        channel = yt.author
        h, m, s = yt.length // 3600, (yt.length % 3600) // 60, yt.length % 60
        duration = f"{h}:{m:02}:{s:02}" if h else (f"{m}:{s:02}" if m else f"{s}")
        return jsonify(
            {
                "title": title,
                "thumbnail": thumbnail,
                "channel": channel,
                "duration": duration,
            }
        )
    except Exception as e:
        return jsonify({"message": "Video info not found", "log": str(e)}), 404


@app.route("/api/progress", methods=["POST"])
def return_progress():
    return jsonify({"progress": 0})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
