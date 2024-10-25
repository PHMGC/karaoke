from process import *

url = "https://www.youtube.com/watch?v=ZbZSe6N_BXs"  # Happy
url2 = "https://www.youtube.com/watch?v=M-mtdN6R3bQ"  # I know im not alone (30s song)
url3 = "https://www.youtube.com/watch?v=Qz52N7gsths&list=RDMMQz52N7gsths&start_radio=1"  # What i was made for (Billie Eilish)
url4 = "https://www.youtube.com/watch?v=QwoF1-1QgwA&list=RDMMQz52N7gsths&index=5"  # a french girl singing je te laisserai des mots while it's raining :')
url5 = "https://www.youtube.com/watch?v=i4FQJ7Qi14o&pp=ygUebm9zc2FzIGhpc3RvcmlhcyBjaGFybGllIGJyb3du"  # dias de luta
url6 = "https://www.youtube.com/watch?v=kLpH1nSLJSs"  # AMORFODA
url7 = "https://www.youtube.com/watch?v=EelX_LwPHbA"  # Carla Bruni - Quelqu'un m'a dit
url8 = "https://www.youtube.com/watch?v=doLMt10ytHY"  # es/jap


def run_everything(url):
    get_video(url)
    uid = extract_uid(url)
    demucs_transcript(uid)
    whisper_transcript(uid)
    # generate_video(uid)


if __name__ == "__main__":
    run_everything(url8)
