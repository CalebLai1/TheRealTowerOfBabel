import tkinter as tk
from tkinter import messagebox
import threading
import numpy as np
import queue
import time
from audio_handler import AudioHandler

class AudioControls:
    def __init__(self, root, audio_handler, transcription_handler, record_button, test_input_button, test_output_button, timer_label, transcription_timer_label, flash_label, chunk_size_slider):
        self.root = root
        self.audio_handler = audio_handler
        self.transcription_handler = transcription_handler
        self.record_button = record_button
        self.test_input_button = test_input_button
        self.test_output_button = test_output_button
        self.timer_label = timer_label
        self.transcription_timer_label = transcription_timer_label
        self.flash_label = flash_label
        self.chunk_size_slider = chunk_size_slider
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.audio_buffer = np.array([], dtype=np.float32)

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
        overlap_duration = 0.3
        overlap_samples = int(self.audio_handler.sample_rate * overlap_duration)

        while self.is_recording:
            try:
                if not self.audio_queue.empty():
                    audio_chunk = self.audio_queue.get()
                    self.audio_buffer = np.append(self.audio_buffer, audio_chunk.flatten())

                    elapsed_time = len(self.audio_buffer) / self.audio_handler.sample_rate
                    self.root.after(0, self.update_timer, elapsed_time)

                    if len(self.audio_buffer) >= chunk_samples:
                        chunk_to_process = self.audio_buffer[:chunk_samples]

                        start_time = time.time()
                        transcription = self.transcription_handler.transcribe_audio_chunk(
                            chunk_to_process,
                            sample_rate=self.audio_handler.sample_rate,
                            channels=self.audio_handler.channels
                        )
                        transcription_time = time.time() - start_time
                        self.root.after(0, self.update_transcription_timer, transcription_time)

                        if transcription:
                            translation = self.translate_text(transcription)
                            self.root.after(0, self.update_transcription_text, transcription)
                            self.root.after(0, self.update_translation_text, translation)

                        self.audio_buffer = self.audio_buffer[-overlap_samples:]
                        self.root.after(0, self.update_timer, 0.0)
                        self.root.after(0, self.flash_reset_label)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error in processing audio: {e}")
                self.is_recording = False
                self.record_button.config(text="Start Recording", bg="#5E81AC")
                break

    def update_timer(self, elapsed_time):
        self.timer_label.config(text=f"Chunk Timer: {elapsed_time:.2f}s")
        self.timer_label.update()

    def update_transcription_timer(self, transcription_time):
        self.transcription_timer_label.config(text=f"Transcription Time: {transcription_time:.2f}s")
        self.transcription_timer_label.update()

    def flash_reset_label(self):
        self.flash_label.config(fg="red")
        self.root.after(200, lambda: self.flash_label.config(fg=self.fg_color))

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

    def translate_text(self, text):
        try:
            translation_language = LANGUAGES[self.translation_language_var.get()]
            translator = GoogleTranslator(source='auto', target=translation_language)
            translated_text = translator.translate(text)
            return translated_text
        except Exception as e:
            print(f"Translation error: {e}")
            return "Translation failed"

    def update_transcription_text(self, text):
        if text.strip():
            self.transcription_text_box.insert(tk.END, text.strip() + " ")
            self.transcription_text_box.see(tk.END)

    def update_translation_text(self, text):
        if text.strip():
            self.translation_text_box.insert(tk.END, text.strip() + " ")
            self.translation_text_box.see(tk.END)