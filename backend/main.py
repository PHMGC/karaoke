import threading, queue
from flask import request, jsonify, Response, json

from process import *
from config import app, db


@app.route("/api/video/info", methods=["POST"])
def post_video_info():
    url = request.json.get("url")
    if not url:
        return jsonify({"message": "URL is required"}), 400
    try:
        video_info = get_video_info(url)
    except Exception as e:
        return jsonify({"message": "Could not get info on given url", "error": str(e)}), 400
    
    return jsonify(video_info)


@app.route("/api/video/karaoke", methods=["POST"])
def karaoke_process():
    url = request.json.get("url")
    if not url:
        return jsonify({"message": "URL is required"}), 400
    try:
        karaoke_process(url)
        return Response(karaoke_process(url), content_type="text/event-stream")
    
    except Exception as e:
        return jsonify({"message": "Error on processing karoke", "error": str(e), "url": url}), 400
    
def karaoke_process(url):
    uid = extract_uid(url)
    if not db.session.query(VideoInfo).filter_by(uid=uid).first():
        q = queue.Queue()
        thread = threading.Thread(target=initiate_karaoke, args=(url, q))
        thread.start()
        while True:
            try:
                data = q.get(timeout=1)
                yield f"data: {json.dumps(data)}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps(data)}\n\n"
                break
    else:
        yield {
            "progress": 100,
            "videoUrl": url,
            "error": None
        }


def initiate_karaoke(url, q : queue.Queue):
    data = {
        "progress": 0,
        "videoUrl": url,
        "error": None
    }
    try:
        info = get_video_info(url)
        get_video(url)
        uid = info["uid"]
        data["progress"] = 10
        q.put(data)
        demucs_transcript(uid)
        data["progress"] = 25
        q.put(data)
        whisper_q = queue.Queue()
        whisper_thread = threading.Thread(target=whisper_transcript, args=(uid, whisper_q))
        whisper_thread.start()
        while True:
            try:
                whisper_progress = whisper_q.get(timeout=1)
                data["progress"] += whisper_progress/2 # whisper only occupies 50% of the total progress
                q.put(data)
            except queue.Empty:
                break
        generate_video(uid)
        data["progress"] = 100
        q.put(data)

    except Exception as e:
        data["error"] = str(e)
        q.put(data)
        return

    infodb = VideoInfo(uid=uid, title=info["title"], channel=info["channel"], duration=info["duration"])
    db.session.add(infodb)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
