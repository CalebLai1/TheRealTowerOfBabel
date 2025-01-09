import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sounddevice as sd
import soundfile as sf
import whisper
from deep_translator import GoogleTranslator
import requests
import time
import torch
import numpy as np
import ttkbootstrap as ttk

class WhisperCloneApp:
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root

        self.style = ttk.Style(theme="solar")

        self.cuda_available = torch.cuda.is_available()
        self.device = "cuda" if self.cuda_available else "cpu"

        self.whisper_models = {
            "tiny": "tiny",
            "base": "base",
            "small": "small",
            "medium": "medium",
            "large": "large"
        }
        self.whisper_model_var = tk.StringVar(value="base")
        self.whisper_model = whisper.load_model(self.whisper_model_var.get()).to(self.device)

        self.input_audio_folder = "whisper_input_audio"
        if not os.path.exists(self.input_audio_folder):
            os.makedirs(self.input_audio_folder)

        self.translation_language_var = tk.StringVar(value="English")
        self.translation_languages = self.get_google_translate_languages()
        self.elevenlabs_api_key = tk.StringVar()
        self.elevenlabs_voice_id = tk.StringVar()
        self.audio_files = []

        self.sequential_playback_active = False
        self.sequential_playback_thread = None
        self.stop_sequential_playback = threading.Event()

        self.is_recording = False
        self.recording_thread = None
        self.recording_data = None
        self.fs = 16000

        self.setup_gui()

    def get_google_translate_languages(self):
        languages = GoogleTranslator().get_supported_languages(as_dict=True)
        return {lang.capitalize(): code for lang, code in languages.items()}

    def setup_gui(self):
        self.parent.grid_rowconfigure(0, weight=0)
        self.parent.grid_rowconfigure(1, weight=0)
        self.parent.grid_rowconfigure(2, weight=0)
        self.parent.grid_rowconfigure(3, weight=0)
        self.parent.grid_rowconfigure(4, weight=1)
        self.parent.grid_rowconfigure(5, weight=0)

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)
        self.parent.grid_columnconfigure(3, weight=1)
        self.parent.grid_columnconfigure(4, weight=1)
        self.parent.grid_columnconfigure(5, weight=1)

        title_label = ttk.Label(self.parent, text="Tower of Babel", font=("Helvetica", 16, "bold"))
        title_label.grid(column=0, row=0, columnspan=6, padx=10, pady=10, sticky='nsew')

        self.setup_transcription_section()
        self.setup_translation_section()
        self.setup_elevenlabs_section()

    def setup_transcription_section(self):
        transcription_label = ttk.Label(self.parent, text="Whisper Transcription Controls", font=("Helvetica", 14, "bold"))
        transcription_label.grid(column=0, row=1, columnspan=3, padx=10, pady=5, sticky='nsew')

        model_label = ttk.Label(self.parent, text="Select Whisper Model:")
        model_label.grid(column=0, row=2, padx=10, pady=2, sticky='w')

        self.model_combo = ttk.Combobox(self.parent, textvariable=self.whisper_model_var, state="readonly")
        self.model_combo['values'] = list(self.whisper_models.keys())
        self.model_combo.grid(column=1, row=2, padx=10, pady=2, sticky='w')
        self.model_combo.bind("<<ComboboxSelected>>", self.update_whisper_model)

        upload_button = ttk.Button(self.parent, text="Upload Audio", command=self.upload_audio)
        upload_button.grid(column=0, row=3, padx=10, pady=5, sticky='w')

        self.record_button = ttk.Button(self.parent, text="Start Recording", command=self.toggle_recording)
        self.record_button.grid(column=1, row=3, padx=10, pady=5, sticky='w')

        clear_button = ttk.Button(self.parent, text="Clear Transcription", command=self.clear_transcription)
        clear_button.grid(column=2, row=3, padx=10, pady=5, sticky='w')

        self.transcription_area = scrolledtext.ScrolledText(self.parent, wrap=tk.WORD, state='disabled')
        self.transcription_area.grid(column=0, row=4, columnspan=3, padx=10, pady=5, sticky='nsew')

    def update_whisper_model(self, event=None):
        selected_model = self.whisper_model_var.get()
        self.whisper_model = whisper.load_model(selected_model).to(self.device)
        messagebox.showinfo("Model Updated", f"Whisper model changed to {selected_model}.")

    def setup_translation_section(self):
        translation_label = ttk.Label(self.parent, text="Translation Controls", font=("Helvetica", 14, "bold"))
        translation_label.grid(column=3, row=1, columnspan=3, padx=10, pady=5, sticky='nsew')

        translation_language_label = ttk.Label(self.parent, text="Select Translation Language:")
        translation_language_label.grid(column=3, row=2, padx=10, pady=2, sticky='w')

        self.translation_language_combo = ttk.Combobox(self.parent, textvariable=self.translation_language_var, state="normal")
        self.translation_language_combo['values'] = list(self.translation_languages.keys())
        self.translation_language_combo.grid(column=4, row=2, padx=10, pady=2, sticky='w')

        clear_translation_button = ttk.Button(self.parent, text="Clear Translation", command=self.clear_translation)
        clear_translation_button.grid(column=3, row=3, padx=10, pady=2, sticky='w')

        self.translation_area = scrolledtext.ScrolledText(self.parent, wrap=tk.WORD, state='disabled')
        self.translation_area.grid(column=3, row=4, columnspan=3, padx=10, pady=5, sticky='nsew')

    def setup_elevenlabs_section(self):
        elevenlabs_label = ttk.Label(self.parent, text="11labs Output", font=("Helvetica", 14, "bold"))
        elevenlabs_label.grid(column=0, row=5, columnspan=6, padx=10, pady=5, sticky='nsew')

        api_key_label = ttk.Label(self.parent, text="11labs API Key:")
        api_key_label.grid(column=0, row=6, padx=10, pady=2, sticky='w')

        self.api_key_entry = ttk.Entry(self.parent, textvariable=self.elevenlabs_api_key, width=30)
        self.api_key_entry.grid(column=1, row=6, padx=10, pady=2, sticky='w')

        voice_id_label = ttk.Label(self.parent, text="Voice ID:")
        voice_id_label.grid(column=2, row=6, padx=10, pady=2, sticky='w')

        self.voice_id_entry = ttk.Entry(self.parent, textvariable=self.elevenlabs_voice_id, width=30)
        self.voice_id_entry.grid(column=3, row=6, padx=10, pady=2, sticky='w')

        self.audio_grid_frame = ttk.Frame(self.parent)
        self.audio_grid_frame.grid(column=0, row=7, columnspan=6, padx=10, pady=5, sticky='nsew')

        self.sequential_playback_button = ttk.Button(
            self.parent,
            text="Play All Sequentially (Off)",
            command=self.toggle_sequential_playback
        )
        self.sequential_playback_button.grid(column=0, row=8, padx=10, pady=10, sticky='w')

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.config(text="Start Recording")
            messagebox.showinfo("Recording", "Recording stopped.")
        else:
            self.is_recording = True
            self.record_button.config(text="Stop Recording")
            self.recording_data = []
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()
            messagebox.showinfo("Recording", "Recording started. Speak now.")

    def record_audio(self):
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.recording_data.append(indata.copy())
            else:
                raise sd.CallbackStop()

        try:
            with sd.InputStream(samplerate=self.fs, channels=1, dtype='int16', callback=callback):
                while self.is_recording:
                    sd.sleep(100)

            if self.recording_data:
                recording = np.concatenate(self.recording_data)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                file_path = os.path.join(self.input_audio_folder, f"recording_{timestamp}.wav")
                sf.write(file_path, recording, self.fs)
                messagebox.showinfo("Recording", f"Recording saved as '{file_path}'.")
                self.transcribe_audio(file_path)
            else:
                messagebox.showwarning("Warning", "No audio data recorded.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during recording: {e}")

    def upload_audio(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac")]
        )
        if file_path:
            self.transcribe_audio(file_path)

    def transcribe_audio(self, file_path):
        try:
            result = self.whisper_model.transcribe(file_path)
            transcription_text = result["text"]

            self.transcription_area.configure(state='normal')
            self.transcription_area.insert(tk.END, f"Transcription:\n{transcription_text}\n\n")
            self.transcription_area.configure(state='disabled')
            self.transcription_area.see(tk.END)

            self.translate_text(transcription_text)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during transcription: {e}")

    def translate_text(self, text):
        try:
            selected_language_name = self.translation_language_var.get()
            target_language = self.translation_languages.get(selected_language_name.capitalize(), "en")
            translator = GoogleTranslator(source='auto', target=target_language)
            translated_text = translator.translate(text)
            self.translation_area.configure(state='normal')
            self.translation_area.insert(tk.END, f"{translated_text}\n")
            self.translation_area.configure(state='disabled')
            self.translation_area.see(tk.END)
            self.generate_elevenlabs_audio(translated_text)
        except Exception as e:
            messagebox.showerror("Translation Error", f"An error occurred during translation: {e}")

    def generate_elevenlabs_audio(self, text):
        api_key = self.elevenlabs_api_key.get()
        voice_id = self.elevenlabs_voice_id.get()

        if not api_key or not voice_id:
            messagebox.showwarning("Warning", "Please enter your 11labs API key and voice ID.")
            return

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                audio_file = f"output_{len(self.audio_files) + 1}.mp3"
                with open(audio_file, "wb") as f:
                    f.write(response.content)
                self.audio_files.append(audio_file)
                self.update_audio_grid()

                if self.sequential_playback_active:
                    self.play_audio_file(audio_file)
            else:
                messagebox.showerror("Error", f"Failed to generate audio: {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating audio: {e}")

    def update_audio_grid(self):
        for widget in self.audio_grid_frame.winfo_children():
            widget.destroy()

        for i, audio_file in enumerate(self.audio_files):
            audio_frame = ttk.Frame(self.audio_grid_frame)
            audio_frame.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky='nsew')

            play_button = ttk.Button(audio_frame, text=f"Play {i + 1}", command=lambda f=audio_file: self.play_audio_file(f))
            play_button.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

            delete_button = ttk.Button(audio_frame, text="X", command=lambda f=audio_file: self.delete_audio_file(f))
            delete_button.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

            download_button = ttk.Button(audio_frame, text="Download", command=lambda f=audio_file: self.download_audio_file(f))
            download_button.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

    def delete_audio_file(self, file_path):
        try:
            os.remove(file_path)
            self.audio_files.remove(file_path)
            self.update_audio_grid()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while deleting the audio file: {e}")

    def play_audio_file(self, file_path):
        try:
            data, fs = sf.read(file_path, dtype='int16')
            sd.play(data, fs)
            sd.wait()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during playback: {e}")

    def download_audio_file(self, file_path):
        try:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("MP3 Files", "*.mp3")],
                title="Save Audio File"
            )
            if save_path:
                import shutil
                shutil.copy(file_path, save_path)
                messagebox.showinfo("Success", f"Audio file saved as {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save audio file: {e}")

    def toggle_sequential_playback(self):
        if self.sequential_playback_active:
            self.sequential_playback_active = False
            self.stop_sequential_playback.set()
            self.sequential_playback_button.config(text="Play All Sequentially (Off)")
        else:
            self.sequential_playback_active = True
            self.stop_sequential_playback.clear()
            self.sequential_playback_button.config(text="Play All Sequentially (On)")

            if self.audio_files:
                self.play_all_sequentially()

    def play_all_sequentially(self):
        if not self.sequential_playback_active:
            return

        def play_next(index):
            if index < len(self.audio_files) and self.sequential_playback_active:
                file_path = self.audio_files[index]
                try:
                    data, fs = sf.read(file_path, dtype='int16')
                    sd.play(data, fs)
                    sd.wait()
                    self.root.after(0, lambda: play_next(index + 1))
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred during playback: {e}")
            elif index >= len(self.audio_files):
                self.root.after(1000, lambda: play_next(index))

        play_next(0)

    def clear_transcription(self):
        self.transcription_area.configure(state='normal')
        self.transcription_area.delete('1.0', tk.END)
        self.transcription_area.configure(state='disabled')

    def clear_translation(self):
        self.translation_area.configure(state='normal')
        self.translation_area.delete('1.0', tk.END)
        self.translation_area.configure(state='disabled')