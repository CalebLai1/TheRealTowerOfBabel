# components/text_boxes.py

import tkinter as tk
from tkinter import scrolledtext

class TextBoxes:
    def __init__(self, root):
        self.root = root

        # TTS Audio Chunks Box (New Box)
        self.tts_audio_box = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            width=30,  # Adjust width as needed
            height=15,
            font=("Helvetica", 12),
            bg="#3B4252",
            fg="#D8DEE9",
            insertbackground="#D8DEE9",
            selectbackground="#5E81AC"
        )
        self.tts_audio_box.pack(side=tk.LEFT, padx=10, expand=True, fill='both')

        # Transcription Text Box
        self.transcription_text_box = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            width=50,
            height=15,
            font=("Helvetica", 12),
            bg="#3B4252",
            fg="#D8DEE9",
            insertbackground="#D8DEE9",
            selectbackground="#5E81AC"
        )
        self.transcription_text_box.pack(side=tk.LEFT, padx=10, expand=True, fill='both')

        # Translation Text Box
        self.translation_text_box = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            width=50,
            height=15,
            font=("Helvetica", 12),
            bg="#3B4252",
            fg="#D8DEE9",
            insertbackground="#D8DEE9",
            selectbackground="#5E81AC"
        )
        self.translation_text_box.pack(side=tk.LEFT, padx=10, expand=True, fill='both')