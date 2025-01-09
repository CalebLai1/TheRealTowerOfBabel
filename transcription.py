# transcription.py
import tkinter as tk
import threading
import queue
import sounddevice as sd
import json
from tkinter import messagebox

class TranscriptionManager:
    def __init__(self, gui):
        self.gui = gui
        self.transcribing = False
        self.audio_queue = queue.Queue()
        self.transcription_thread = None
        self.stop_event = threading.Event()

    def start_transcription(self):
        if self.transcribing:
            messagebox.showinfo("Info", "Already transcribing.")
            return

        if not self.gui.model_handler.model:
            messagebox.showinfo("Info", "Please load the model first.")
            return

        self.transcribing = True
        self.stop_event.clear()
        self.gui.transcription_area.configure(state='normal')
        self.gui.transcription_area.delete('1.0', tk.END)
        self.gui.transcription_area.configure(state='disabled')

        self.transcription_thread = threading.Thread(target=self.transcribe)
        self.transcription_thread.start()
        messagebox.showinfo("Info", "Start speaking now. Transcription has begun.")

    def stop_transcription(self):
        if not self.transcribing:
            messagebox.showinfo("Info", "Not currently transcribing.")
            return

        self.stop_event.set()
        self.transcribing = False
        messagebox.showinfo("Info", "Transcription stopped.")

    def transcribe(self):
        def callback(indata, frames, time_info, status):
            if self.stop_event.is_set():
                raise sd.CallbackStop()
            self.audio_queue.put(bytes(indata))

        try:
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=callback
            ):
                while not self.stop_event.is_set():
                    data = self.audio_queue.get()
                    if self.gui.model_handler.recognizer.AcceptWaveform(data):
                        result = self.gui.model_handler.recognizer.Result()
                        result_dict = json.loads(result)
                        text = result_dict.get("text", "")
                        if text:
                            self.gui.update_transcription(text, final=True)
                    else:
                        partial_result = self.gui.model_handler.recognizer.PartialResult()
                        partial_dict = json.loads(partial_result)
                        partial = partial_dict.get("partial", "")
                        if partial:
                            self.gui.update_transcription(partial, final=False)
        except Exception as e:
            self.transcribing = False
            messagebox.showerror("Error", f"An error occurred during transcription: {e}")
