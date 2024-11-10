import threading
import queue
from flask import request, jsonify, Response, json, send_file, abort

from process import *
from config import app, db
from models import VideoInfo

from threading import Thread, Lock

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

data_folder = "data"
max_dur_m = 20  # min

progress_data = {}
process_lock = Lock()


admin = Admin(app, name='Meu Admin', template_mode='bootstrap3')
admin.add_view(ModelView(VideoInfo, db.session))


@app.route("/api/carousel", methods=["GET"])
def carousel():
    # size = request.json.get("size")
    size = 10
    db_entries = VideoInfo.query.all()[:size]
    results = [
        {
            "uid": entry.uid,
            "title": entry.title,
            "thumbnail": entry.thumbnail,
            "channel": entry.channel,
            "duration": entry.duration,
        }
        for entry in db_entries
    ]
    return jsonify(results)


@app.route("/api/video/info", methods=["POST"])
def post_video_info():
    url = request.json.get("prompt")
    if not url:
        error = {"error": "Url is required", "url": url}
        print(error)
        return jsonify(error), 400
    try:
        return jsonify(get_video_info(url))

    except Exception as e:
        error = {"error": "Could not get info on given url",
                 "traceback": str(e.with_traceback())}
        print(error)
        return jsonify(error), 400
    
@app.route("/api/videos/info", methods=["POST"])
def post_videos_info():
    prompt = request.json.get("prompt")
    if not prompt:
        error = {"error": "Prompt is required", "prompt": prompt}
        print(error)
        return jsonify(error), 400
    try:
        return jsonify(search_video_info(prompt))

    except Exception as e:
        error = {"error": "Could not get info on given prompt",
                 "traceback": str(e.with_traceback())}
        print(error)
        return jsonify(error), 400


@app.route("/api/video/karaoke", methods=["POST"])
def karaoke_route():
    url = request.json.get("url")
    if not url:
        error = {"error": "URL is required"}
        print(error)
        return jsonify(error), 400
    uid = extract_uid(url)
    try:
        videoInfo = VideoInfo.query.filter_by(uid=uid).first()
        if not videoInfo and uid not in progress_data:
            thread = Thread(target=karaoke_process, args=(url,))
            thread.start()
            return Response(json.dumps({"uid": uid, "videoPath": None}))

        elif videoInfo.error is not None:
            thread = Thread(target=karaoke_process, args=(url,))
            thread.start()
            return Response(json.dumps({"uid": uid, "videoPath": None}))
        else:
            video_path = f"/api/video/karaoke/{uid}/video"
            return Response(json.dumps({"uid": uid, "videoPath": video_path}))

    except Exception as e:
        print(e.with_traceback())
        error = {"error": "Error on processing karaoke",
                 "traceback": str(e.with_traceback()), "url": url}
        print(error)
        return jsonify(error), 400


@app.route("/api/video/karaoke/<uid>", methods=["GET"])
def karaoke_progress(uid=None):
    print(f"Received UID: {uid}")
    if not uid:
        error = {"error": "UID is required"}
        print(error)
        return jsonify(error), 400
    video_path = f"/api/video/karaoke/{uid}/video"

    def generate():
        while True:
            if uid in progress_data:
                progress = progress_data[uid]
                # Check if processing is done
                if progress >= 100:
                    yield f"data: {json.dumps({'progress': 100, 'videoPath': video_path, 'error': None})}\n\n"
                    break  # End the stream if complete

                # Yield the current progress
                yield f"data: {json.dumps({'progress': progress, 'videoPath': video_path, 'error': None})}\n\n"
            else:
                # If the uid is not in process_data, we can yield a default value
                yield f"data: {json.dumps({'progress': 0, 'videoPath': video_path, 'error': None})}\n\n"

            time.sleep(1)  # Wait for a bit before the next update

    return Response(generate(), content_type='text/event-stream')


@app.route("/api/video/karaoke/<uid>/video", methods=["GET"])
def serve_video_by_uid(uid):
    video_path = os.path.join(data_folder, uid, "final_video.mp4")
    try:
        return send_file(video_path, mimetype='video/mp4')
    except FileNotFoundError:
        print("Video not found")
        abort(404, description="Video not found")


def karaoke_process(url):
    with process_lock:
        uid = extract_uid(url)
        get_video(url, data_folder)
        progress_data[uid] = 10
        demucs_transcript(uid, data_folder)
        progress_data[uid] = 25
        whisper_q = queue.Queue()
        whisper_thread = threading.Thread(
            target=whisper_transcript, args=(uid, data_folder, whisper_q))
        whisper_thread.start()
        while True:
            try:
                whisper_progress = whisper_q.get(timeout=1)
                print("whisper_progress", whisper_progress)
                # whisper only occupies 50% of the total progress
                progress_data[uid] += whisper_progress/2

            except queue.Empty:
                break
        whisper_thread.join()
        progress_data[uid] = 75
        generate_video(uid, data_folder)
        progress_data[uid] = 100

        # if successfull, than add to db
        with app.app_context():
            info = get_video_info(url)
            infodb = VideoInfo(
                uid=uid, title=info["title"], thumbnail=info["thumbnail"], channel=info["channel"], duration=info["duration"])
            db.session.add(infodb)
            db.session.commit()

        cleanup(uid, data_folder)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
