# audio_handler.py

import sounddevice as sd
import numpy as np
import wave
import os
from datetime import datetime
import threading
from tkinter import messagebox
import queue

class AudioHandler:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels

    def populate_audio_devices(self, input_dropdown, output_dropdown):
        """Populate the input and output device dropdowns with unique identifiers."""
        devices = sd.query_devices()
        input_devices = [f"[{i}] {d['name']}, {sd.query_hostapis(d['hostapi'])['name']}" 
                         for i, d in enumerate(devices) if d['max_input_channels'] > 0]
        output_devices = [f"[{i}] {d['name']}, {sd.query_hostapis(d['hostapi'])['name']}" 
                          for i, d in enumerate(devices) if d['max_output_channels'] > 0]
        
        input_dropdown["values"] = input_devices
        output_dropdown["values"] = output_devices
        
        if input_devices:
            input_dropdown.current(0)
        if output_devices:
            output_dropdown.current(0)

    def start_recording_stream(self, input_device_index, audio_queue, is_recording_flag):
        """Start the audio input stream using device index."""
        try:
            with sd.InputStream(
                device=input_device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=lambda indata, frames, time_info, status: audio_queue.put(indata.copy())
            ):
                while is_recording_flag.is_set():
                    sd.sleep(100)
        except Exception as e:
            messagebox.showerror("Audio Error", f"Failed to start audio stream:\n{e}")

    def test_audio_input(self, input_device, output_device, sample_rate):
        """Record a short audio clip and play it back to test input."""
        def record_and_play():
            try:
                duration = 3  # seconds
                messagebox.showinfo("Test Audio Input", "Recording will start for 3 seconds.")
                recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=self.channels, device=input_device)
                sd.wait()  # Wait until recording is finished
                messagebox.showinfo("Test Audio Input", "Recording finished. Playing back the recording.")
                sd.play(recording, samplerate=sample_rate, device=output_device)
                sd.wait()  # Wait until playback is finished
                messagebox.showinfo("Test Audio Input", "Playback finished.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during audio input test:\n{e}")
        
        threading.Thread(target=record_and_play, daemon=True).start()

    def test_audio_output(self, output_device, sample_rate):
        """Play a predefined test sound to test output."""
        def play_test_sound():
            try:
                duration = 2  # seconds
                frequency = 440  # Hz (A4 note)
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                test_sound = 0.5 * np.sin(2 * np.pi * frequency * t)
                messagebox.showinfo("Test Audio Output", "Playing test sound (A4 tone).")
                sd.play(test_sound, samplerate=sample_rate, device=output_device)
                sd.wait()  # Wait until playback is finished
                messagebox.showinfo("Test Audio Output", "Test sound playback finished.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during audio output test:\n{e}")
        
        threading.Thread(target=play_test_sound, daemon=True).start()
