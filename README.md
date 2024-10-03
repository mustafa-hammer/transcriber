# transcriber

## To get it going

- Install these:
  - ollama
    - add llama3.1 model
    - [Install](https://ollama.com/download/mac)
  - brew install portaudio
  - brew install python-tk@3.11
  - HuggingFace token
    - `export HGTOKEN=xyz` into your Python venv
  - [Speaker diarization setup](https://huggingface.co/pyannote/speaker-diarization-3.1#requirements) 
  - Have a way to record audio from your PC
    - Blackhole instructions (TODO)
  - Create a python venv and install requirements.txt
  - Change folder path in `transcriber_ui.py`

# Links
 - [Whisper Models](https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages)
 - [Speaker Diarization](https://huggingface.co/pyannote/speaker-diarization-3.1)
