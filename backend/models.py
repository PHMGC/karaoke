from config import db
#import json


class VideoInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(200), unique=True, nullable=False)
    title = db.Column(db.String(200), unique=False, nullable=False)
    channel = db.Column(db.String(200), unique=False, nullable=False)
    duration = db.Column(db.String(200), unique=False, nullable=False)
    error = db.Column(db.String(200), unique=False, nullable=True)

    # def response(self):
    #     return json.dumps({
    #         "uid": self.uid,
    #         "error": self.error
    #     })
