# transcription_handler.py

import whisper
import torch
import wave
import os
from datetime import datetime
from tkinter import messagebox
import numpy as np  # <-- Added import

class TranscriptionHandler:
    def __init__(self, language_code="en", use_cuda=False):
        self.language_code = language_code
        self.use_cuda = use_cuda
        self.model = whisper.load_model("base")
        
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
            with wave.open(temp_file, 'w') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(sample_rate)
                wf.writeframes((audio_buffer * 32767).astype(np.int16).tobytes())  # np is now defined
            
            # Transcribe audio
            result = self.model.transcribe(
                temp_file,
                language=self.language_code,
                fp16=self.use_cuda
            )
            
            return result["text"].strip()
        
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
        
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
