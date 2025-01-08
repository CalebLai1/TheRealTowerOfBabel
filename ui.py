# ui.py

import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox
from audio_handler import AudioHandler
from transcription_handler import TranscriptionHandler
from constants import LANGUAGES
import threading
import queue
import numpy as np
import time
import torch
from deep_translator import GoogleTranslator

class VoiceTypingAppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Voice Typing")
        self.root.geometry("900x800")
        self.audio_handler = AudioHandler()
        self.transcription_handler = TranscriptionHandler()
        self.use_cuda = torch.cuda.is_available()
        if self.use_cuda:
            self.transcription_handler.update_model("base", use_cuda=True)
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.audio_buffer = np.array([], dtype=np.float32)
        self.setup_ui()

    def setup_ui(self):
        self.bg_color = "#2E3440"
        self.fg_color = "#D8DEE9"
        self.accent_color = "#5E81AC"
        self.text_bg_color = "#3B4252"
        self.root.configure(bg=self.bg_color)
        self.custom_font = font.Font(family="Helvetica", size=12)

        # Create a frame for the text boxes
        text_frame = tk.Frame(self.root, bg=self.bg_color)
        text_frame.pack(padx=20, pady=20, expand=True, fill='both')

        # Transcription Text Box
        self.transcription_text_box = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=50,
            height=15,
            font=self.custom_font,
            bg=self.text_bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.accent_color
        )
        self.transcription_text_box.pack(side=tk.LEFT, padx=10, expand=True, fill='both')

        # Translation Text Box
        self.translation_text_box = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=50,
            height=15,
            font=self.custom_font,
            bg=self.text_bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.accent_color
        )
        self.translation_text_box.pack(side=tk.LEFT, padx=10, expand=True, fill='both')

        # Create control buttons frame
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10)

        # Start/Stop Recording button
        self.record_button = tk.Button(
            button_frame,
            text="Start Recording",
            command=self.toggle_recording,
            width=15,
            height=2,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.record_button.pack(side=tk.LEFT, padx=10)

        # Clear Text button
        self.clear_button = tk.Button(
            button_frame,
            text="Clear Text",
            command=self.clear_text,
            width=15,
            height=2,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # Test Audio Input button
        self.test_input_button = tk.Button(
            button_frame,
            text="Test Audio Input",
            command=self.test_audio_input,
            width=15,
            height=2,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.test_input_button.pack(side=tk.LEFT, padx=10)

        # Test Audio Output button
        self.test_output_button = tk.Button(
            button_frame,
            text="Test Audio Output",
            command=self.test_audio_output,
            width=15,
            height=2,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.test_output_button.pack(side=tk.LEFT, padx=10)

        # Add a dropdown for Whisper model
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(
            button_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            font=self.custom_font,
            state="readonly",
            width=10
        )
        self.model_dropdown.set("base")
        self.model_dropdown.pack(side=tk.LEFT, padx=10)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.change_model)

        # Add a dropdown for input language
        self.language_var = tk.StringVar()
        self.language_dropdown = ttk.Combobox(
            button_frame,
            textvariable=self.language_var,
            values=list(LANGUAGES.keys()),
            font=self.custom_font,
            state="readonly",
            width=15
        )
        self.language_dropdown.set("English")
        self.language_dropdown.pack(side=tk.LEFT, padx=10)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.change_language)

        # Add a dropdown for translation language
        self.translation_language_var = tk.StringVar()
        self.translation_language_dropdown = ttk.Combobox(
            button_frame,
            textvariable=self.translation_language_var,
            values=list(LANGUAGES.keys()),
            font=self.custom_font,
            state="readonly",
            width=15
        )
        self.translation_language_dropdown.set("Spanish")  # Default translation language
        self.translation_language_dropdown.pack(side=tk.LEFT, padx=10)
        self.translation_language_dropdown.bind("<<ComboboxSelected>>", self.change_translation_language)

        # Slider for chunk size
        slider_frame = tk.Frame(self.root, bg=self.bg_color)
        slider_frame.pack(pady=10)
        self.chunk_size_slider = tk.Scale(
            slider_frame,
            from_=0.1,
            to=10.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            label="Chunk Size (seconds)",
            length=300,
            bg=self.bg_color,
            fg=self.fg_color,
            troughcolor=self.text_bg_color,
            highlightbackground=self.bg_color,
            font=self.custom_font,
            sliderrelief=tk.FLAT,
            activebackground=self.accent_color,
            command=self.update_chunk_size_from_slider
        )
        self.chunk_size_slider.set(3.0)
        self.chunk_size_slider.pack(side=tk.LEFT, padx=10)

        # Entry for precise chunk size input
        self.chunk_size_entry = tk.Entry(
            slider_frame,
            width=5,
            font=self.custom_font,
            bg=self.text_bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.chunk_size_entry.insert(0, "3.0")
        self.chunk_size_entry.pack(side=tk.LEFT, padx=10)

        # Apply button for chunk size
        self.apply_button = tk.Button(
            slider_frame,
            text="Apply",
            command=self.update_chunk_size_from_entry,
            width=5,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.apply_button.pack(side=tk.LEFT, padx=10)

        # Device selection frame
        device_frame = tk.Frame(self.root, bg=self.bg_color)
        device_frame.pack(pady=10)
        self.input_device_var = tk.StringVar()
        self.input_device_label = tk.Label(
            device_frame,
            text="Input Device:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.input_device_label.pack(side=tk.LEFT, padx=10)
        self.input_device_dropdown = ttk.Combobox(
            device_frame,
            textvariable=self.input_device_var,
            font=self.custom_font,
            state="readonly",
            width=50
        )
        self.input_device_dropdown.pack(side=tk.LEFT, padx=10)
        self.output_device_var = tk.StringVar()
        self.output_device_label = tk.Label(
            device_frame,
            text="Output Device:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.output_device_label.pack(side=tk.LEFT, padx=10)
        self.output_device_dropdown = ttk.Combobox(
            device_frame,
            textvariable=self.output_device_var,
            font=self.custom_font,
            state="readonly",
            width=50
        )
        self.output_device_dropdown.pack(side=tk.LEFT, padx=10)
        self.audio_handler.populate_audio_devices(self.input_device_dropdown, self.output_device_dropdown)

        # Add a progress bar for chunk processing visualization
        self.progress_frame = tk.Frame(self.root, bg=self.bg_color)
        self.progress_frame.pack(pady=10)

        self.progress_label = tk.Label(
            self.progress_frame,
            text="Chunk Progress:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.progress_label.pack(side=tk.LEFT, padx=10)

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode="determinate"
        )
        self.progress_bar.pack(side=tk.LEFT, padx=10)

        # Initialize progress bar value
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = 100  # Represents 100% of the chunk duration

        # Add a flashing label for chunk reset visualization
        self.flash_label = tk.Label(
            self.progress_frame,
            text="Chunk Reset",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.flash_label.pack(side=tk.LEFT, padx=10)

    def update_progress_bar(self, value):
        """Update the progress bar to the given value."""
        self.progress_bar["value"] = value
        self.progress_bar.update()

    def flash_reset_label(self):
        """Flash the label to indicate a chunk reset."""
        self.flash_label.config(fg="red")
        self.root.after(200, lambda: self.flash_label.config(fg=self.fg_color))

    def update_chunk_size_from_slider(self, value):
        self.chunk_duration = float(value)
        self.chunk_size_entry.delete(0, tk.END)
        self.chunk_size_entry.insert(0, str(self.chunk_duration))

    def update_chunk_size_from_entry(self):
        try:
            value = float(self.chunk_size_entry.get())
            if 0.1 <= value <= 10.0:
                self.chunk_duration = value
                self.chunk_size_slider.set(self.chunk_duration)
            else:
                messagebox.showerror("Invalid Value", "Chunk size must be between 0.1 and 10.0 seconds.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def clear_text(self):
        self.transcription_text_box.delete(1.0, tk.END)
        self.translation_text_box.delete(1.0, tk.END)
        messagebox.showinfo("Text Cleared", "The text boxes have been cleared.")

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
            self.transcription_handler.update_language(LANGUAGES[self.language_var.get()])
            self.transcription_handler.update_model(self.model_var.get(), use_cuda=self.use_cuda)
            messagebox.showinfo("Microphone Ready", "The microphone is ready. Start speaking.")
            self.recording_thread = threading.Thread(target=self.start_recording, daemon=True)
            self.recording_thread.start()
            self.processing_thread = threading.Thread(target=self.process_audio, daemon=True)
            self.processing_thread.start()

    def start_recording(self):
        selected_input = self.input_device_var.get()
        selected_output = self.output_device_var.get()
        if not selected_input:
            messagebox.showerror("Input Device Error", "No input device selected.")
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg=self.accent_color)
            return
        try:
            device_index = int(selected_input.split(']')[0].strip('['))
        except (IndexError, ValueError):
            messagebox.showerror("Device Selection Error", "Invalid input device selection.")
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg=self.accent_color)
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

    def change_model(self, event):
        selected_model = self.model_var.get()
        self.transcription_handler.update_model(selected_model, use_cuda=self.use_cuda)

    def change_language(self, event):
        selected_language = self.language_var.get()
        language_code = LANGUAGES[selected_language]
        self.transcription_handler.update_language(language_code)

    def change_translation_language(self, event):
        pass  # No action needed here, as translation language is used directly in translate_text

    def run(self):
        self.root.mainloop()    