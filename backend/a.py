from process import *

url = "https://www.youtube.com/watch?v=ZbZSe6N_BXs"  # Happy
url2 = "https://www.youtube.com/watch?v=M-mtdN6R3bQ"  # I know im not alone (30s song)

get_video(url)
uid = extract_uid(url)
demucs_transcript(uid)
whisper_transcript(uid)
generate_video(uid)
