import whisper
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import utils
from jinja2 import Environment, FileSystemLoader
import warnings
import ollama

def transcribe(audio_filepath, whisper_model_size):
    
    # model = whisper.load_model(whisper_model_size, weights_only=True)
    # Suppress the FutureWarning related to torch.load
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        model = whisper.load_model(whisper_model_size)

    print('Generating transcript')
    asr_result = model.transcribe(audio_filepath, fp16=False)
    
    # transcript = asr_result['text']
    # print('Transcript:', transcript)
    
    return(asr_result)

class PrintProgressHook(ProgressHook):
    def on_epoch_start(self, epoch: int, total_epochs: int, **kwargs):
        print(f"Starting epoch {epoch}/{total_epochs}")
    
    def on_batch_end(self, batch_idx: int, total_batches: int, **kwargs):
        print(f"Processed batch {batch_idx}/{total_batches}")

def diarization(audio_filepath, hg_token):
    warnings.filterwarnings("ignore", category=UserWarning)
    
    print('Generating diarization')
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hg_token)
    
    # Use the custom progress hook
    with PrintProgressHook() as hook:
        diarization_result = pipeline(audio_filepath, hook=hook)
    
    return diarization_result
    
def combine_transcribe_diarization(asr_result, diarization_result):
    final_result = utils.diarize_text(asr_result, diarization_result)

    print('Combining transcribe and diarization')
    transcript = []
    for seg, spk, sent in final_result:
        line = f'{seg.start:.2f} {seg.end:.2f} {spk} {sent}'
        transcript.append(line)
    return transcript

def write_to_file(meeting_note_filepath, transcript, title, date):
    # Create an environment for Jinja2 templates
    env = Environment(loader=FileSystemLoader('.'))

    # Load the template file
    template = env.get_template('template.md')
    transcript_string = "\n".join(transcript)

    # Data to fill into the template
    data = {
        'title': title,
        'date': date,
        'transcript': transcript_string
    }

    # Render the template with data
    output = template.render(data)

    # Write the rendered output to a new Markdown file
    output_filename = meeting_note_filepath
    with open(output_filename, 'w') as f:
        f.write(output)    

def summarize_transcript_in_file(meeting_note_filepath):
    # Read the transcript from the file
    with open(meeting_note_filepath, 'r') as f:
        content = f.read()
    print("Generating summary")
    
    # Isolate the transcript (assuming it's the main content)
    transcript = content.split("## Summary")[0].strip()

    # Use Ollama to summarize the transcript
    summary = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'user',
            'content': f"""I will provide you a transcript from a meeting.
                        I want you to summarize and fill in these sections in Markdown: 
                        ### General summary ### Summary for each speaker. You can identify each speaker in the transcript by SPEAKER_XX where XX is the number. 
                        The output from here will go to a Markdown document so dont add anything that is not a summary, 
                        thank you. Do not attempt to interpret tone or social dynamics, keep the summary dry. Here is the {transcript}""" 
        },
        ])
    print("Summary generated")
    # Append the summary to the file
    with open(meeting_note_filepath, 'a') as f:
        f.write("\n\n## Summary\n")  
        f.write(summary['message']['content'])
