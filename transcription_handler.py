# transcription_handler.py

import whisper
import torch
import wave
import os
from datetime import datetime
from tkinter import messagebox
import numpy as np

class TranscriptionHandler:
    def __init__(self, language_code="en", use_cuda=False):
        self.language_code = language_code
        self.use_cuda = use_cuda
        self.model = whisper.load_model("base")  # Default model

        if self.use_cuda and torch.cuda.is_available():
            self.model = self.model.cuda()

    def update_model(self, model_size, use_cuda=False):
        """Update the Whisper model based on user selection."""
        self.use_cuda = use_cuda
        self.model = whisper.load_model(model_size)
        if self.use_cuda and torch.cuda.is_available():
            self.model = self.model.cuda()

    def update_language(self, language_code):
        """Update the language for transcription."""
        self.language_code = language_code

    def transcribe_audio_chunk(self, audio_buffer, sample_rate, channels):
        """Transcribe a chunk of audio."""
        temp_file = f"temp_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        try:
            # Normalize the audio buffer to avoid clipping
            audio_buffer = audio_buffer / np.max(np.abs(audio_buffer))

            # Write the audio buffer to a temporary WAV file
            with wave.open(temp_file, 'w') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(sample_rate)
                wf.writeframes((audio_buffer * 32767).astype(np.int16).tobytes())

            # Transcribe the audio using Whisper
            result = self.model.transcribe(
                temp_file,
                language=self.language_code,
                fp16=self.use_cuda,
                no_speech_threshold=0.5,  # Adjust sensitivity to avoid misinterpreting silence
                logprob_threshold=-0.5,   # Adjust to filter out low-confidence transcriptions
            )

            # Clean up the temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

            return result["text"].strip()

        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def cleanup(self):
        """Clean up any temporary files or resources."""
        temp_files = [f for f in os.listdir() if f.startswith("temp_audio_")]
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except Exception as e:
                print(f"Error cleaning up temporary file {temp_file}: {e}")