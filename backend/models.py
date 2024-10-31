from config import db


class VideoInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(200), unique=True, nullable=False)
    title = db.Column(db.String(200), unique=False, nullable=False)
    channel = db.Column(db.String(200), unique=False, nullable=False)
    duration = db.Column(db.String(200), unique=False, nullable=False)
    progress = db.Column(db.Float, unique=False, nullable=False)

    def to_json(self):
        return {
            "uid": self.uid,
            "title": self.title,
            "channel": self.channel,
            "duration": self.duration,
            "progress": self.progress,
        }
