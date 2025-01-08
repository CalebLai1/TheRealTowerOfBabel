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
        self.transcription_handler = TranscriptionHandler(use_cuda=True)
        self.use_cuda = torch.cuda.is_available()
        if self.use_cuda:
            self.transcription_handler.update_model("small", use_cuda=True)
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

        text_frame = tk.Frame(self.root, bg=self.bg_color)
        text_frame.pack(padx=20, pady=20, expand=True, fill='both')

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

        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10)

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

        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(
            button_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            font=self.custom_font,
            state="readonly",
            width=10
        )
        self.model_dropdown.set("small")
        self.model_dropdown.pack(side=tk.LEFT, padx=10)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.change_model)

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

        self.translation_language_var = tk.StringVar()
        self.translation_language_dropdown = ttk.Combobox(
            button_frame,
            textvariable=self.translation_language_var,
            values=list(LANGUAGES.keys()),
            font=self.custom_font,
            state="readonly",
            width=15
        )
        self.translation_language_dropdown.set("Spanish")
        self.translation_language_dropdown.pack(side=tk.LEFT, padx=10)
        self.translation_language_dropdown.bind("<<ComboboxSelected>>", self.change_translation_language)

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
        self.chunk_size_slider.set(2.0)
        self.chunk_size_slider.pack(side=tk.LEFT, padx=10)

        self.chunk_size_entry = tk.Entry(
            slider_frame,
            width=5,
            font=self.custom_font,
            bg=self.text_bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.chunk_size_entry.insert(0, "2.0")
        self.chunk_size_entry.pack(side=tk.LEFT, padx=10)

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

        self.timer_frame = tk.Frame(self.root, bg=self.bg_color)
        self.timer_frame.pack(pady=10)

        self.timer_label = tk.Label(
            self.timer_frame,
            text="Chunk Timer: 0.00s",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.timer_label.pack(side=tk.LEFT, padx=10)

        self.transcription_timer_label = tk.Label(
            self.timer_frame,
            text="Transcription Time: 0.00s",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.transcription_timer_label.pack(side=tk.LEFT, padx=10)

        self.flash_label = tk.Label(
            self.timer_frame,
            text="Chunk Reset",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.flash_label.pack(side=tk.LEFT, padx=10)

    def update_timer(self, elapsed_time):
        self.timer_label.config(text=f"Chunk Timer: {elapsed_time:.2f}s")
        self.timer_label.update()

    def update_transcription_timer(self, transcription_time):
        self.transcription_timer_label.config(text=f"Transcription Time: {transcription_time:.2f}s")
        self.transcription_timer_label.update()

    def flash_reset_label(self):
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
        pass

    def run(self):
        self.root.mainloop()