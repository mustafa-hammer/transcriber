# transcriber

## What is this?

A local Python application that does the following:
- Record audio, you'll need to provide the application with an Audio device that contains both your mic and system audio. This can be done using [BlackHole](https://existential.audio/blackhole/).
- Transcibe using [Whisper model](https://github.com/openai/whisper)  
- Speaker diarization
- Summarize using Ollama and llama3.1
- You can also link a local audio file to transcribe and summarize

## To get it going

- Install these:
  - ffmpeg
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
  - You need a local folder called `transcriber` with two sub folders called `notes` and `audio`

# Links
 - [Whisper Models](https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages)
 - [Speaker Diarization](https://huggingface.co/pyannote/speaker-diarization-3.1)
