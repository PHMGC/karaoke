from flask import request, jsonify, Response

from process import *
from config import app, db


progress = 10


@app.route("/api/video/info", methods=["POST"])
def post_video_info():
    url = request.json.get("url")
    video_info = get_video_info(url)
    if video_info is None:
        return jsonify({"message": "Could not get info on given url"}), 400
    return jsonify(video_info)


def increase_progress():
    global progress
    progress += 20
    return progress


@app.route("/api/progress")
def send_progress():
    return Response(
        f"data: {increase_progress()}\n\n", content_type="text/event-stream"
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
