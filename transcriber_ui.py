import tkinter as tk
from recorder import Recorder
import audio_devices
from datetime import datetime
import transcriber
import os
import time 
import threading

# Load env variables
hg_token = os.environ["HGTOKEN"]
whisper_model_size = "base.en"

folder = "/Users/mustafa.elhilo/transcriber/"
notes = folder + "notes/"
audio = folder + "record/"

def start_timer():
    global elapsed_time, timer_running

    elapsed_time = 0  
    timer_running = True 
    while timer_running:
        elapsed_time += 1  
        timer_label.config(text=f"Timer: {elapsed_time} s")
        timer_label.update() 
        time.sleep(1)  

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
        print('Recording already running')
    else:
        # Get selected device from the UI
        device_id = selected_device.get()
        
        # Create a timestamped filename for the recording
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{audio}{audio_record_filename.get()}_{timestamp}.wav"

        # Check if device_id is valid
        if device_id.isdigit():
            device_id = int(device_id)
            print(f"Selected audio device: {device_id}")

            # Initialize Recorder object if not already done
            rec = Recorder(channels=2)

            # Open the recording file with audio device
            record_running = rec.open(filename, audio_device=device_id, mode='wb')

            # Start recording
            record_running.start_recording(audio_device=device_id)

            # Change button color to indicate recording
            button_rec.config(fg='red')  # Change to red for recording
            
            # Start the timer in a separate thread
            threading.Thread(target=start_timer, daemon=True).start()
        else:
            print('Invalid device selection')


           
def stop():
    global record_running, timer_running

    if record_running is not None:
        record_running.stop_recording()
        record_running.close()
        record_running = None
        print('Audio recorder stopped')

        # Reset button color and stop timer
        button_rec.config(bg='SystemButtonFace', fg='black')
        timer_label.config(text="Timer: 0 s")
        timer_running = False  # Stop the timer
    else:
        print('Audio recorder is not running')

def transcribe_only():
    global transcribe_running, audio_record_filename
    if transcribe_running is not None:
        print('transcribe_only already running')
    else:
        transcribe_running = 'running'
        transcript = transcriber.transcribe(filename, whisper_model_size)
        file_namepath = F"{notes}{audio_record_filename.get()}_{timestamp}.md"
        transcriber.write_to_file(file_namepath, transcript, audio_record_filename.get(), timestamp)

def transcribe_and_diarization():
    global transcribe_and_diarization_running, audio_record_filename
    if transcribe_and_diarization_running is not None:
        print('transcribe_and_diarization already running')
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
        print('Summarize already running')
    else:
        summarize_running = 'running'
        file_namepath = F"{notes}{audio_record_filename.get()}_{timestamp}.md"
        transcriber.summarize_transcript_in_file(file_namepath)
       
def manual_audio():
    global transcribe_and_diarization_running, manual_filename
    
    if transcribe_and_diarization_running is not None:
        print('Manual transcribe and diarization already running')
    else:
        file_path = manual_filename.get()
        file_name = os.path.basename(manual_filename.get())
        name = os.path.splitext(file_name)[0] 
        note_file_path = file_path.replace("/record/", "/notes/")
        note_file_path = note_file_path.replace(".wav", ".md")

        print(note_file_path)
        transcribe_and_diarization_running = 'running'
        transcript = transcriber.transcribe(file_path, whisper_model_size)
        diarization = transcriber.diarization(file_path, hg_token)
        combine = transcriber.combine_transcribe_diarization(transcript, diarization)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        transcriber.write_to_file(note_file_path, combine, name, timestamp)

def manual_summarize():
    global summarize_running, manual_filename
    file_path = manual_filename.get()
    note_file_path = file_path.replace("/record/", "/notes/")
    note_file_path = note_file_path.replace(".wav", ".md")

    if summarize_running is not None:
        print('Summarize already running')
    else:
        summarize_running = 'running'
        transcriber.summarize_transcript_in_file(note_file_path)


# rec = recorder.Recorder(channels=2)
record_running = None
transcribe_running = None
transcribe_and_diarization_running = None
summarize_running = None

timer_running = False
elapsed_time = 0

root = tk.Tk()
root.title("Transcriber3000")
root.geometry('900x900')

# Audio filename
filename_label=tk.StringVar()
filename_label.set("Meeting Name:")
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

timer_label = tk.Label(root, text="Timer: 0 s")
timer_label.grid(row=4, column=2)

button_stop = tk.Button(root, text='Stop Audio Record', command=stop)
button_stop.grid(row=5, column=1)

transcribe = tk.Button(root, text='Transcribe Only', command=transcribe_only)
transcribe.grid(row=6, column=1)

transcribe_and_speaker = tk.Button(root, text='Transcribe and Speakers', command=transcribe_and_diarization)
transcribe_and_speaker.grid(row=7, column=1)

summarize = tk.Button(root, text='Summarize', command=summarize)
summarize.grid(row=8, column=1)

# Manual audio filename
manual_filename_label=tk.StringVar()
manual_filename_label.set("Enter filename location:")
manual_filename_value=tk.Label(root, textvariable=manual_filename_label, height=4)
manual_filename_value.grid(row=9, column=1)

manual_audio_record_filename = tk.StringVar()
manual_filename = tk.Entry(root, textvariable=manual_audio_record_filename)
manual_filename.grid(row=9, column=2)
manual_transcribe_and_speaker = tk.Button(root, text='Transcribe and Speakers', command=manual_audio)
manual_transcribe_and_speaker.grid(row=9, column=3)
manual_summarize = tk.Button(root, text='Summarize', command=manual_summarize)
manual_summarize.grid(row=9, column=4)
root.mainloop()
