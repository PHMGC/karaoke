import sys

from process import *
from config import db, app
from models import VideoInfo

url = "https://www.youtube.com/watch?v=ZbZSe6N_BXs"  # Happy
# I know im not alone (30s song)
url2 = "https://www.youtube.com/watch?v=M-mtdN6R3bQ"
# What i was made for (Billie Eilish)
url3 = "https://www.youtube.com/watch?v=Qz52N7gsths&list=RDMMQz52N7gsths&start_radio=1"
# a french girl singing je te laisserai des mots while it's raining :')
url4 = "https://www.youtube.com/watch?v=QwoF1-1QgwA&list=RDMMQz52N7gsths&index=5"
url5 = "https://www.youtube.com/watch?v=i4FQJ7Qi14o"  # dias de luta
url6 = "https://www.youtube.com/watch?v=kLpH1nSLJSs"  # AMORFODA
# Carla Bruni - Quelqu'un m'a dit
url7 = "https://www.youtube.com/watch?v=EelX_LwPHbA"
url8 = "https://www.youtube.com/watch?v=doLMt10ytHY"  # es/jap

data_folder = "data"


def debug_process(url):
    uid = extract_uid(url)
    get_video(url, data_folder)
    demucs_transcript(uid, data_folder)
    whisper_transcript(uid, data_folder)
    generate_video(uid, data_folder, True)


def update_db():
    with app.app_context():
        print("updating db")

        db.drop_all()
        db.create_all()
        for name in os.listdir(data_folder):
            if os.path.isdir(os.path.join(data_folder, name)):
                info = get_video_info_uid(name)
                infodb = VideoInfo(
                    uid=name, title=info["title"], thumbnail=info["thumbnail"], channel=info["channel"], duration=info["duration"])
                db.session.add(infodb)

        db.session.commit()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "debug_process":
            debug_process()
        elif sys.argv[1] == "update_db":
            update_db()
        else:
            print("wrong args")
