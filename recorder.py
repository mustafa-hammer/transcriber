import pyaudio
import wave
import numpy as np

class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, audio_device, mode='wb'):
        return RecordingFile(fname, mode, audio_device, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(object):
    def __init__(self, fname, mode, audio_device, channels, 
                rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.audio_device= audio_device
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration, audio_device):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        input_device_index=audio_device,
                                        frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self, audio_device):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        input_device_index=audio_device,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

def convert_to_stereo_audio(input_file, output_file):
    '''Function to normalize mono or stereo WAV files by duplicating the content of both channels 
       (or the mono channel) into a stereo format.'''
    
    with wave.open(input_file, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16)

        # Check if the audio is stereo (2 channels)
        if wf.getnchannels() == 2:
            # Reshape to separate the channels
            audio_data = audio_data.reshape(-1, 2)

            # Take the average of the two channels and duplicate it across both channels
            mixed_data = np.mean(audio_data, axis=1).astype(np.int16)
            new_audio_data = np.column_stack((mixed_data, mixed_data)).ravel()
        elif wf.getnchannels() == 1:
            # Mono audio: duplicate the single channel into both left and right
            new_audio_data = np.column_stack((audio_data, audio_data)).ravel()
        else:
            print("Unsupported number of channels:", wf.getnchannels())
            return

        # Open a new wave file to write the normalized stereo data
        with wave.open(output_file, 'wb') as output_wf:
            output_wf.setnchannels(2)
            output_wf.setsampwidth(wf.getsampwidth())
            output_wf.setframerate(wf.getframerate())
            output_wf.writeframes(new_audio_data.tobytes())
