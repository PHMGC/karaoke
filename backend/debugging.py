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


def processtest(prompt=None):
    if not prompt:
        prompt = url2
    search = search_video_info(prompt)
    uid = search["uid"]
    url = 'https://www.youtube.com/watch?v=' + uid
    get_video(url, data_folder)
    demucs_transcript(uid, data_folder)
    whisper_transcript(uid, data_folder)
    generate_video(uid, data_folder, True)
    #cleanup(uid, data_folder)


def updatedb():
    with app.app_context():
        print("updating db")

        db.drop_all()
        db.create_all()
        for name in os.listdir(data_folder):
            if os.path.isdir(os.path.join(data_folder, name)):
                info = search_video_info(name)
                infodb = VideoInfo(
                    uid=name, title=info["title"], thumbnail=info["thumbnail"], channel=info["channel"], duration=info["duration"])
                db.session.add(infodb)

        db.session.commit()


def testYT(prompt):
    result = search_video_info(prompt)

    print(result[0])


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "processtest":
            if len(sys.argv) > 2:
                processtest(" ".join(sys.argv[2:]))
            else:
                processtest()
            return
        elif sys.argv[1] == "updatedb":
            updatedb()
            return
        elif sys.argv[1] == "testYT":
            if len(sys.argv) > 2:
                testYT(" ".join(sys.argv[2:]))
            return
    print("wrong args")


if __name__ == "__main__":
    main()
