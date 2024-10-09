import whisper
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import utils
from jinja2 import Environment, FileSystemLoader
import warnings
import ollama
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

summary_model_name = "llama3.1"
summary_chunk_size = 9000
summary_chunk_overlap = 500

def transcribe(audio_filepath, whisper_model_size):
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        model = whisper.load_model(whisper_model_size)

    print('Generating transcript')
    asr_result = model.transcribe(audio_filepath, fp16=False)
    print('Completed: Generating transcript')
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
    
    print('Completed: Generating diarization')

    return diarization_result
    
def combine_transcribe_diarization(asr_result, diarization_result):
    final_result = utils.diarize_text(asr_result, diarization_result)

    print('Combining transcribe and diarization')
    transcript = []
    for seg, spk, sent in final_result:
        line = f'{seg.start:.2f} {seg.end:.2f} {spk} {sent}'
        transcript.append(line)
    print('Completed: Combining transcribe and diarization')
    return transcript

def write_to_file(meeting_note_filepath, transcript, title, date):
    env = Environment(loader=FileSystemLoader('.'))

    # Load the template file
    template = env.get_template('template.md')

    if isinstance(transcript, str):
        # print(transcript)
        transcript_string = transcript
    elif isinstance(transcript, list):
        transcript_string = "\n".join(transcript)
    else:
        print("Unsupported data type to write to file")

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
    print(f"Completed: Writing to file: {meeting_note_filepath}")

def summarize_transcript_in_chunks(file_path):
    llama_model = Ollama(model = summary_model_name)
    transcript = extract_transcript(file_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size = summary_chunk_size, chunk_overlap = summary_chunk_overlap)
    chunks = text_splitter.split_text(transcript)

    prompt_template = """
    You will be given a chunk of a transcript from a meeting:

    {text}

    Summarize the meeting as if you are taking notes during the meeting. Keep it concise. Don't attempt to create any groupings. 
    I expect bullet points as if you are in the meeting writing notes as the speaker talks. I don't need to know who said what.
    Identify any clearly defined action items. You should provide me with two lists the summary and the action items. 
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    # Create an LLM chain to process each chunk and generate a summary
    chain = LLMChain(llm=llama_model, prompt=prompt)


    # Summarize each chunk and store the results
    summaries = []
    for i, chunk in enumerate(chunks):
        print(f"Summarizing chunk {i+1}/{len(chunks)}...")
        summary_dict = chain.invoke({"text": chunk})
        
        # Extract the summary text from the response dictionary
        summary_text = summary_dict.get('text', '')
        summaries.append(summary_text)

    # Join all chunk summaries into a final summary
    final_summary = "\n".join(summaries)
    return final_summary

def write_summary_to_notes(content, meeting_note_filepath):
    with open(meeting_note_filepath, 'a') as f:
        f.write("\n\n## Summary\n")  
        f.write(content)

def summarize_transcript_from_chunks(content):
    # Read the transcript from the file

    print("Generating summary")

    # Isolate the transcript (assuming it's the main content)
    transcript = content

    messages = [
        {
            'role': 'system',
            'content': """
                        Act as a helpful assistant. 
                        Your task is to summarize the key points from the provided meeting notes. 
                        The summary should be concise yet comprehensive, capturing the essence of the meeting. 
                        Your summary should enable someone who wasn't present at the meeting to understand its outcomes and next steps clearly. 
                        The only sections in the summary should be: 
                        - Highlights: a 400 word summary of the meeting in bullet points. If it makes sense you can group some of the topics in this section. The title of this section is ### Highlights
                        - Notes: a detailed summary of the meeting in bullet point form. Should read as the meeting has progressed. The title of this section is ### Notes
                        Format everything in Markdown and don't add any fluff. I don't want your openion on tone of anyone, be direct.  
                        """
        },
        {
            'role': 'user',
            'content': f"""
                        Here are my meeting notes: {transcript}""" 
        }
    ]
    summary = ollama.chat(model=summary_model_name, messages=messages)
    print("Completed: Generating summary")
    return summary


def extract_transcript(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    transcript = []
    in_transcript = False
    for line in lines:
        if "## Transcript:" in line:
            in_transcript = True
            continue
        elif line.startswith("#") and in_transcript:
            break
        if in_transcript:
            transcript.append(line.strip())

    return "\n".join(transcript)

def file_name_formatting(input_string):
    return input_string.replace(' ', '_').replace('/', '_')
