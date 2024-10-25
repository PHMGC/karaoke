import sys, tqdm
import torch, whisper, whisper.transcribe


class _CustomProgressBar(tqdm.tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current = self.n  # Set the initial value

    def update(self, n):
        super().update(n)
        self._current += n

        # Handle progress here
        print(f"{self._current}/{self.total}")


transcribe_module = sys.modules["whisper.transcribe"]
transcribe_module.tqdm.tqdm = _CustomProgressBar
device = "cuda" if torch.cuda.is_available() else "cpu"

model = whisper.load_model("medium", device={device})
model.transcribe(sys.argv[0])
