# audio_handler.py
import sounddevice as sd
import soundfile as sf
import threading
import time
from tkinter import messagebox
import os

class AudioHandler:
    def __init__(self, gui):
        self.gui = gui
        self.test_recording_file = 'test_recording.wav'

    def record_audio(self):
        duration = 5  # seconds
        fs = 16000  # Sample rate
        try:
            messagebox.showinfo("Recording", f"Recording for {duration} seconds...")
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            file_path = os.path.join(self.gui.input_audio_folder, f"recording_{timestamp}.wav")
            sf.write(file_path, recording, fs)
            messagebox.showinfo("Recording", f"Recording completed and saved as '{file_path}'.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during recording: {e}")

    def play_audio(self):
        if not os.path.exists(self.test_recording_file):
            messagebox.showerror("Error", f"No recording found. Please record audio first.")
            return

        try:
            data, fs = sf.read(self.test_recording_file, dtype='int16')
            sd.play(data, fs)
            sd.wait()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during playback: {e}")
