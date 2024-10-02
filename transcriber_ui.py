import tkinter as tk
import recorder
import audio_devices
from datetime import datetime
import transcriber
import os

# Load env variables
# export HGTOKEN=xyz
hg_token = os.environ["HGTOKEN"]
whisper_model_size = "base.en"

folder = "/Users/mustafa.elhilo/transcriber/"
notes = folder + "notes/"
audio = folder + "record/"


def devices():
    device_list = audio_devices.list_audio_devices()

    # Clear the listbox first
    listbox_devices.delete(0, tk.END)
    
    # Populate the listbox with the devices
    for device in device_list:
        # listbox_devices.insert(tk.END, f"Input Device id {device['id']} - {device['name']}")
        listbox_devices.insert(tk.END, f"Input Device id {device['id']} - {device['name']}")

def start():
    global record_running, selected_device, audio_record_filename, filename, timestamp

    if record_running is not None:
        print('already running')
    else:
        device_id = selected_device.get()
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{audio}{audio_record_filename.get()}_{timestamp}.wav"

        print(filename)
        if device_id.isdigit():
            device_id = int(device_id)
            print(f"Selected audio device: {device_id}")
            record_running = rec.open(filename, audio_device=device_id, mode='wb')
            record_running.start_recording()
        else:
            print('Invalid device selection')
           
def stop():
    global record_running

    if record_running is not None:
        record_running.stop_recording()
        record_running.close()
        record_running = None
        print('Audio recorder stopped')
    else:
        print('Audio recorder is not running')

def transcribe_only():
    global transcribe_running, audio_record_filename
    if transcribe_running is not None:
        print('already running')
    else:
        transcribe_running = 'running'
        transcript = transcriber.transcribe(filename, whisper_model_size)
        file_namepath = F"{notes}{audio_record_filename.get()}_{timestamp}.md"
        transcriber.write_to_file(file_namepath, transcript, audio_record_filename.get(), timestamp)

def transcribe_and_diarization():
    global transcribe_and_diarization_running, audio_record_filename
    if transcribe_and_diarization_running is not None:
        print('already running')
    else:
        transcribe_and_diarization_running = 'running'
        transcript = transcriber.transcribe(filename, whisper_model_size)
        diarization = transcriber.diarization(filename, hg_token)
        combine = transcriber.combine_transcribe_diarization(transcript, diarization)

        file_namepath = F"{notes}{audio_record_filename.get()}_{timestamp}.md"

        transcriber.write_to_file(file_namepath, combine, audio_record_filename.get(), timestamp)

def summarize():
    global summarize_running, audio_record_filename
    if summarize_running is not None:
        print('already running')
    else:
        summarize_running = 'running'
        file_namepath = F"{notes}{audio_record_filename.get()}_{timestamp}.md"
        summary = transcriber.summarize_transcript_in_file(file_namepath)
       

rec = recorder.Recorder(channels=1)
record_running = None
transcribe_running = None
transcribe_and_diarization_running = None
summarize_running = None

root = tk.Tk()
root.title("Transcriber3000")
root.geometry('800x500')

# Audio filename
filename_label=tk.StringVar()
filename_label.set("Enter Meeting Name:")
filename_value=tk.Label(root, textvariable=filename_label, height=4)
filename_value.grid(row=1, column=1)

audio_record_filename = tk.StringVar()
filename = tk.Entry(root, textvariable=audio_record_filename)
filename.grid(row=1, column=2)

# Button to list devices
button_devices_list = tk.Button(root, text='List Audio Devices', command=devices)
button_devices_list.grid(row=2, column=1)

# Listbox to display audio devices
listbox_devices = tk.Listbox(root, width=50)
listbox_devices.grid(row=2, column=2)

# Entry box to select a device by its ID
selected_device_label=tk.StringVar()
selected_device_label.set("Enter Audio Device ID:")
audio_device_value=tk.Label(root, textvariable=selected_device_label, height=4)
audio_device_value.grid(row=3, column=1)

selected_device = tk.StringVar()
device_entry = tk.Entry(root, textvariable=selected_device)
device_entry.grid(row=3, column=2)

button_rec = tk.Button(root, text='Start Audio Record', command=start)
button_rec.grid(row=4, column=1)

button_stop = tk.Button(root, text='Stop Audio Record', command=stop)
button_stop.grid(row=5, column=1)

transcribe = tk.Button(root, text='Transcribe Only', command=transcribe_only)
transcribe.grid(row=6, column=1)

transcribe_and_speaker = tk.Button(root, text='Transcribe and Speakers', command=transcribe_and_diarization)
transcribe_and_speaker.grid(row=7, column=1)

summarize = tk.Button(root, text='Summarize', command=summarize)
summarize.grid(row=8, column=1)

root.mainloop() 

