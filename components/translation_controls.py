# components/translation_controls.py

import tkinter as tk
from tkinter import ttk
from constants import LANGUAGES

class TranslationControls:
    def __init__(self, root, transcription_handler):
        self.root = root
        self.transcription_handler = transcription_handler

        # Input Language Dropdown
        self.language_var = tk.StringVar()
        self.language_dropdown = ttk.Combobox(
            root,
            textvariable=self.language_var,
            values=list(LANGUAGES.keys()),
            font=("Helvetica", 12),
            state="readonly",
            width=15
        )
        self.language_dropdown.set("English")
        self.language_dropdown.pack(side=tk.LEFT, padx=10)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.change_language)

        # Translation Language Dropdown
        self.translation_language_var = tk.StringVar()
        self.translation_language_dropdown = ttk.Combobox(
            root,
            textvariable=self.translation_language_var,
            values=list(LANGUAGES.keys()),
            font=("Helvetica", 12),
            state="readonly",
            width=15
        )
        self.translation_language_dropdown.set("Spanish")
        self.translation_language_dropdown.pack(side=tk.LEFT, padx=10)
        self.translation_language_dropdown.bind("<<ComboboxSelected>>", self.change_translation_language)

    def change_language(self, event):
        selected_language = self.language_var.get()
        language_code = LANGUAGES[selected_language]
        self.transcription_handler.update_language(language_code)

    def change_translation_language(self, event):
        pass  # No action needed here, as translation language is used directly in translate_text