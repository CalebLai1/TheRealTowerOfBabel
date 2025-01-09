import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from model_handler import ModelHandler
from transcription import TranscriptionManager
from audio_handler import AudioHandler
import os
from deep_translator import GoogleTranslator
import requests
import soundfile as sf
import sounddevice as sd
import ttkbootstrap as ttk

class TranscriptionApp:
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root

        self.style = ttk.Style(theme="solar")

        self.language_var = tk.StringVar(value="English")
        self.size_var = tk.StringVar(value="large")
        self.transcribing = False
        self.model_handler = ModelHandler(self)
        self.transcription_manager = TranscriptionManager(self)
        self.audio_handler = AudioHandler(self)
        self.input_audio_folder = "input_audio"
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

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.parent, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(column=0, row=10, columnspan=8, padx=10, pady=10, sticky='nsew')
        self.progress_bar.grid_remove()

        self.setup_gui()

    def show_progress_bar(self):
        self.progress_bar.grid()
        self.progress_var.set(0)
        self.root.update_idletasks()

    def hide_progress_bar(self):
        self.progress_bar.grid_remove()
        self.progress_var.set(0)
        self.root.update_idletasks()

    def update_progress_bar(self, percent):
        self.progress_var.set(percent)
        self.root.update_idletasks()

    def setup_gui(self):
        self.parent.grid_rowconfigure(0, weight=0)
        self.parent.grid_rowconfigure(1, weight=0)
        self.parent.grid_rowconfigure(2, weight=0)
        self.parent.grid_rowconfigure(3, weight=0)
        self.parent.grid_rowconfigure(4, weight=1)
        self.parent.grid_rowconfigure(5, weight=1)
        self.parent.grid_rowconfigure(6, weight=0)
        self.parent.grid_rowconfigure(7, weight=0)
        self.parent.grid_rowconfigure(8, weight=0)
        self.parent.grid_rowconfigure(9, weight=0)
        self.parent.grid_rowconfigure(10, weight=0)

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)
        self.parent.grid_columnconfigure(3, weight=1)
        self.parent.grid_columnconfigure(4, weight=1)
        self.parent.grid_columnconfigure(5, weight=1)
        self.parent.grid_columnconfigure(6, weight=1)
        self.parent.grid_columnconfigure(7, weight=1)

        title_label = ttk.Label(self.parent, text="Tower of Babel", font=("Helvetica", 16, "bold"))
        title_label.grid(column=0, row=0, columnspan=8, padx=10, pady=10, sticky='nsew')

        self.setup_transcription_section()
        self.setup_translation_section()
        self.setup_elevenlabs_section()
        self.setup_bottom_section()

    def setup_transcription_section(self):
        controls_label = ttk.Label(self.parent, text="Transcription Controls", font=("Helvetica", 14, "bold"))
        controls_label.grid(column=0, row=1, columnspan=3, padx=10, pady=5, sticky='nsew')

        language_label = ttk.Label(self.parent, text="Select Language:")
        language_label.grid(column=0, row=2, padx=5, pady=2, sticky='w')

        self.language_combo = ttk.Combobox(self.parent, textvariable=self.language_var, state="readonly")
        self.language_combo['values'] = list(self.model_handler.vosk_models.keys())
        self.language_combo.grid(column=1, row=2, padx=5, pady=2, sticky='w')

        size_label = ttk.Label(self.parent, text="Select Model Size:")
        size_label.grid(column=0, row=3, padx=5, pady=2, sticky='w')

        self.size_combo = ttk.Combobox(self.parent, textvariable=self.size_var, state="readonly")
        self.size_combo.grid(column=1, row=3, padx=5, pady=2, sticky='w')

        self.update_model_sizes()

        load_button = ttk.Button(self.parent, text="Load Model", command=self.load_model)
        load_button.grid(column=2, row=2, padx=5, pady=2, sticky='w')

        start_button = ttk.Button(self.parent, text="Start Transcribing", command=self.start_transcription)
        start_button.grid(column=0, row=4, padx=5, pady=2, sticky='w')

        stop_button = ttk.Button(self.parent, text="Stop Transcribing", command=self.stop_transcription)
        stop_button.grid(column=1, row=4, padx=5, pady=2, sticky='w')

        clear_transcription_button = ttk.Button(self.parent, text="Clear Transcription", command=self.clear_transcription)
        clear_transcription_button.grid(column=2, row=4, padx=5, pady=2, sticky='w')

        self.transcription_area = scrolledtext.ScrolledText(self.parent, wrap=tk.WORD, state='disabled')
        self.transcription_area.grid(column=0, row=5, columnspan=3, padx=10, pady=5, sticky='nsew')

    def update_model_sizes(self, event=None):
        selected_language = self.language_var.get()
        if selected_language in self.model_handler.vosk_models:
            model_sizes = list(self.model_handler.vosk_models[selected_language].keys())
            self.size_combo['values'] = model_sizes
            if model_sizes:
                self.size_var.set(model_sizes[0])

    def setup_translation_section(self):
        translation_label = ttk.Label(self.parent, text="Translation Controls", font=("Helvetica", 14, "bold"))
        translation_label.grid(column=3, row=1, columnspan=3, padx=10, pady=5, sticky='nsew')

        translation_language_label = ttk.Label(self.parent, text="Select Translation Language:")
        translation_language_label.grid(column=3, row=2, padx=10, pady=2, sticky='w')

        self.translation_language_combo = ttk.Combobox(self.parent, textvariable=self.translation_language_var, state="normal")
        self.translation_language_combo['values'] = list(self.translation_languages.keys())
        self.translation_language_combo.grid(column=4, row=2, padx=10, pady=2, sticky='w')

        clear_translation_button = ttk.Button(self.parent, text="Clear Translation", command=self.clear_translation)
        clear_translation_button.grid(column=5, row=2, padx=10, pady=2, sticky='w')

        self.translation_area = scrolledtext.ScrolledText(self.parent, wrap=tk.WORD, state='disabled')
        self.translation_area.grid(column=3, row=5, columnspan=3, padx=10, pady=5, sticky='nsew')

    def setup_elevenlabs_section(self):
        elevenlabs_label = ttk.Label(self.parent, text="11labs Output", font=("Helvetica", 14, "bold"))
        elevenlabs_label.grid(column=6, row=1, columnspan=2, padx=10, pady=5, sticky='nsew')

        api_key_label = ttk.Label(self.parent, text="11labs API Key:")
        api_key_label.grid(column=6, row=2, padx=10, pady=2, sticky='w')

        self.api_key_entry = ttk.Entry(self.parent, textvariable=self.elevenlabs_api_key, width=30)
        self.api_key_entry.grid(column=7, row=2, padx=10, pady=2, sticky='w')

        voice_id_label = ttk.Label(self.parent, text="Voice ID:")
        voice_id_label.grid(column=6, row=3, padx=10, pady=2, sticky='w')

        self.voice_id_entry = ttk.Entry(self.parent, textvariable=self.elevenlabs_voice_id, width=30)
        self.voice_id_entry.grid(column=7, row=3, padx=10, pady=2, sticky='w')

        self.audio_grid_frame = ttk.Frame(self.parent)
        self.audio_grid_frame.grid(column=6, row=5, columnspan=2, padx=10, pady=5, sticky='nsew')

        self.sequential_playback_button = ttk.Button(
            self.parent,
            text="Play All Sequentially (Off)",
            command=self.toggle_sequential_playback
        )
        self.sequential_playback_button.grid(column=6, row=6, padx=10, pady=10, sticky='w')

    def setup_bottom_section(self):
        mic_test_label = ttk.Label(self.parent, text="Microphone Test", font=("Helvetica", 14, "bold"))
        mic_test_label.grid(column=0, row=7, columnspan=8, padx=10, pady=10, sticky='nsew')

        button_frame = ttk.Frame(self.parent)
        button_frame.grid(column=0, row=8, columnspan=8, padx=10, pady=10, sticky='nsew')

        record_button = ttk.Button(button_frame, text="Record", command=self.audio_handler.record_audio)
        record_button.grid(column=0, row=0, padx=10, pady=10, sticky='w')

        play_button = ttk.Button(button_frame, text="Play", command=self.audio_handler.play_audio)
        play_button.grid(column=1, row=0, padx=10, pady=10, sticky='w')

        progress_label = ttk.Label(self.parent, text="Download Progress", font=("Helvetica", 14, "bold"))
        progress_label.grid(column=0, row=9, columnspan=8, padx=10, pady=10, sticky='nsew')

    def get_google_translate_languages(self):
        languages = GoogleTranslator().get_supported_languages(as_dict=True)
        return {lang.capitalize(): code for lang, code in languages.items()}

    def load_model(self):
        self.model_handler.load_model()

    def start_transcription(self):
        self.transcription_manager.start_transcription()

    def stop_transcription(self):
        self.transcription_manager.stop_transcription()

    def clear_transcription(self):
        self.transcription_area.configure(state='normal')
        self.transcription_area.delete('1.0', tk.END)
        self.transcription_area.configure(state='disabled')

    def clear_translation(self):
        self.translation_area.configure(state='normal')
        self.translation_area.delete('1.0', tk.END)
        self.translation_area.configure(state='disabled')

    def update_transcription(self, text, final=False):
        def append_text():
            self.transcription_area.configure(state='normal')
            if final:
                self.transcription_area.insert(tk.END, f"{text}\n")
                self.translate_text(text)
            else:
                self.transcription_area.delete("end-2l linestart", "end-1c")
                self.transcription_area.insert(tk.END, f"{text}\n")
            self.transcription_area.configure(state='disabled')
            self.transcription_area.see(tk.END)

        self.root.after(0, append_text)

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