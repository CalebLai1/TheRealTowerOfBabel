# components/audio_controls.py

import tkinter as tk
from tkinter import messagebox
import threading
import numpy as np
import queue
import time
from audio_handler import AudioHandler

class AudioControls:
    def __init__(self, root, audio_handler, transcription_handler, record_button, test_input_button, test_output_button):
        self.root = root
        self.audio_handler = audio_handler
        self.transcription_handler = transcription_handler
        self.record_button = record_button
        self.test_input_button = test_input_button
        self.test_output_button = test_output_button
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.audio_buffer = np.array([], dtype=np.float32)

        # Bind buttons to their respective methods
        self.record_button.config(command=self.toggle_recording)
        self.test_input_button.config(command=self.test_audio_input)
        self.test_output_button.config(command=self.test_audio_output)

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg="#5E81AC")
            self.audio_buffer = np.array([], dtype=np.float32)
            while not self.audio_queue.empty():
                self.audio_queue.get()
            messagebox.showinfo("Recording Stopped", "Recording has been stopped and the buffer has been cleared.")
        else:
            self.is_recording = True
            self.record_button.config(text="Stop Recording", bg="#BF616A")
            self.audio_buffer = np.array([], dtype=np.float32)
            messagebox.showinfo("Microphone Ready", "The microphone is ready. Start speaking.")
            self.recording_thread = threading.Thread(target=self.start_recording, daemon=True)
            self.recording_thread.start()
            self.processing_thread = threading.Thread(target=self.process_audio, daemon=True)
            self.processing_thread.start()

    def start_recording(self):
        selected_input = self.input_device_var.get()
        if not selected_input:
            messagebox.showerror("Input Device Error", "No input device selected.")
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg="#5E81AC")
            return
        try:
            device_index = int(selected_input.split(']')[0].strip('['))
        except (IndexError, ValueError):
            messagebox.showerror("Device Selection Error", "Invalid input device selection.")
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg="#5E81AC")
            return
        is_recording_flag = threading.Event()
        is_recording_flag.set()
        self.audio_handler.start_recording_stream(
            input_device_index=device_index,
            audio_queue=self.audio_queue,
            is_recording_flag=is_recording_flag
        )

    def process_audio(self):
        chunk_duration = self.chunk_size_slider.get()
        chunk_samples = int(self.audio_handler.sample_rate * chunk_duration)
        overlap_duration = 0.5  # Overlap duration in seconds (adjust as needed)
        overlap_samples = int(self.audio_handler.sample_rate * overlap_duration)

        while self.is_recording:
            try:
                if not self.audio_queue.empty():
                    audio_chunk = self.audio_queue.get()
                    self.audio_buffer = np.append(self.audio_buffer, audio_chunk.flatten())

                    # Update the progress bar based on the buffer size
                    progress = (len(self.audio_buffer) / chunk_samples) * 100
                    self.root.after(0, self.update_progress_bar, progress)

                    # Process the audio buffer when it reaches the chunk size
                    if len(self.audio_buffer) >= chunk_samples:
                        # Extract the chunk to process
                        chunk_to_process = self.audio_buffer[:chunk_samples]

                        # Transcribe the chunk
                        transcription = self.transcription_handler.transcribe_audio_chunk(
                            chunk_to_process,
                            sample_rate=self.audio_handler.sample_rate,
                            channels=self.audio_handler.channels
                        )

                        if transcription:
                            # Translate the transcription
                            translation = self.translate_text(transcription)

                            # Update the GUI with the transcription and translation
                            self.root.after(0, self.update_transcription_text, transcription)
                            self.root.after(0, self.update_translation_text, translation)

                        # Retain the last `overlap_samples` for the next chunk
                        self.audio_buffer = self.audio_buffer[-overlap_samples:]

                        # Reset the progress bar and flash the label
                        self.root.after(0, self.update_progress_bar, 0)
                        self.root.after(0, self.flash_reset_label)
                else:
                    time.sleep(0.1)  # Sleep briefly to avoid busy-waiting
            except Exception as e:
                print(f"Error in processing audio: {e}")
                self.is_recording = False
                self.record_button.config(text="Start Recording", bg="#5E81AC")
                break

    def test_audio_input(self):
        selected_input = self.input_device_var.get()
        selected_output = self.output_device_var.get()
        sample_rate = self.audio_handler.sample_rate
        if not selected_input or not selected_output:
            messagebox.showerror("Device Selection Error", "Please select both input and output devices for testing.")
            return
        try:
            input_index = int(selected_input.split(']')[0].strip('['))
            output_index = int(selected_output.split(']')[0].strip('['))
        except (IndexError, ValueError):
            messagebox.showerror("Device Selection Error", "Invalid device selection.")
            return
        self.audio_handler.test_audio_input(input_device=input_index, output_device=output_index, sample_rate=sample_rate)

    def test_audio_output(self):
        selected_output = self.output_device_var.get()
        sample_rate = self.audio_handler.sample_rate
        if not selected_output:
            messagebox.showerror("Output Device Error", "No output device selected.")
            return
        try:
            output_index = int(selected_output.split(']')[0].strip('['))
        except (IndexError, ValueError):
            messagebox.showerror("Device Selection Error", "Invalid output device selection.")
            return
        self.audio_handler.test_audio_output(output_device=output_index, sample_rate=sample_rate)