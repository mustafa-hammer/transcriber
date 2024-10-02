from pyannote.audio.pipelines.utils.hook import ProgressHook
from pyannote.audio import Pipeline
import os

hg_token = os.environ["HGTOKEN"]

# Define a custom hook to print progress
class PrintProgressHook(ProgressHook):
    def on_epoch_start(self, epoch: int, total_epochs: int, **kwargs):
        print(f"Starting epoch {epoch}/{total_epochs}")
    
    def on_batch_end(self, batch_idx: int, total_batches: int, **kwargs):
        print(f"Processed batch {batch_idx}/{total_batches}")


pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                    use_auth_token=hg_token)

# Use the custom progress hook to monitor diarization progress
with PrintProgressHook() as hook:
    diarization = pipeline("audio.wav", hook=hook)
