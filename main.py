import tkinter as tk
import ctypes
import sys
from tkinter import ttk
from gui import TranscriptionApp
from whisper_clone_gui import WhisperCloneApp
import ttkbootstrap as ttk

class MainApplication:
    def __init__(self, root):
        if sys.platform == 'win32':
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        root.tk.call('tk', 'scaling', root.winfo_fpixels('1i') / 72.0)
        root.geometry("")
        root.state('zoomed')

        self.style = ttk.Style(theme="solar")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.gui_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.gui_tab, text="Realtime Voice to Translated Voice")
        self.original_gui = TranscriptionApp(self.gui_tab, root)

        self.whisper_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.whisper_tab, text="Prerecorded Voice to Translated Voice")
        self.whisper_gui = WhisperCloneApp(self.whisper_tab, root)

def main():
    root = ttk.Window(themename="solar")
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()