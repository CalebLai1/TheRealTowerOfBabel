import whisper
import torch
import numpy as np
import os
from tkinter import messagebox
from scipy.signal import resample  # Import resample once at the top

class TranscriptionHandler:
    def __init__(self, language_code="en", use_cuda=False):
        self.language_code = language_code
        self.use_cuda = use_cuda
        self.model = whisper.load_model("base")  # Use "base" for better speed-accuracy balance

        if self.use_cuda and torch.cuda.is_available():
            self.model = self.model.cuda()  # Move model to GPU

    def update_model(self, model_size, use_cuda=False):
        """Update the Whisper model based on user selection."""
        self.use_cuda = use_cuda
        self.model = whisper.load_model(model_size)
        if self.use_cuda and torch.cuda.is_available():
            self.model = self.model.cuda()  # Move model to GPU

    def update_language(self, language_code):
        """Update the language for transcription."""
        self.language_code = language_code

    def transcribe_audio_chunk(self, audio_buffer, sample_rate, channels):
        """Transcribe a chunk of audio directly without writing to a file."""
        try:
            # Normalize the audio buffer to avoid clipping
            audio_buffer = audio_buffer / np.max(np.abs(audio_buffer))

            # Resample the audio buffer to 16kHz if necessary (Whisper expects 16kHz audio)
            if sample_rate != 16000:
                num_samples = int(len(audio_buffer) * 16000 / sample_rate)
                audio_buffer = resample(audio_buffer, num_samples)
                sample_rate = 16000

            # Transcribe the audio buffer directly
            result = self.model.transcribe(
                audio_buffer.astype(np.float32),  # Ensure the buffer is in float32 format
                fp16=self.use_cuda,  # Enable fp16 for faster GPU computation
                language=self.language_code,
                no_speech_threshold=0.5,  # Adjust sensitivity to avoid misinterpreting silence
                logprob_threshold=-0.5,   # Adjust to filter out low-confidence transcriptions
            )

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