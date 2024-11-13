import whisperx
from whisperx.utils import WriteSRT

device = "cuda" 
audio_file = "vocals.wav"
batch_size = 16 # reduce if low on GPU mem
compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)

# 1. Transcribe with original whisper (batched)
model = whisperx.load_model("large-v2", device, compute_type=compute_type)

audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)

model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
aligned_result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

with open("vocals.srt", "w", encoding="utf-8") as srt:
    writer = WriteSRT(".")
    writer.write_result(result, srt, {"max_line_width": 10, "max_line_count": 2, "highlight_words": True, "preserve_segments": True})
