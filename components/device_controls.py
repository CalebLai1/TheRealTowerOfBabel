# components/device_controls.py

import tkinter as tk
from tkinter import ttk
from audio_handler import AudioHandler

class DeviceControls:
    def __init__(self, root, audio_handler):
        self.root = root
        self.audio_handler = audio_handler

        # Input Device Dropdown
        self.input_device_var = tk.StringVar()
        self.input_device_label = tk.Label(
            root,
            text="Input Device:",
            bg="#2E3440",
            fg="#D8DEE9",
            font=("Helvetica", 12)
        )
        self.input_device_label.pack(side=tk.LEFT, padx=10)
        self.input_device_dropdown = ttk.Combobox(
            root,
            textvariable=self.input_device_var,
            font=("Helvetica", 12),
            state="readonly",
            width=50
        )
        self.input_device_dropdown.pack(side=tk.LEFT, padx=10)

        # Output Device Dropdown
        self.output_device_var = tk.StringVar()
        self.output_device_label = tk.Label(
            root,
            text="Output Device:",
            bg="#2E3440",
            fg="#D8DEE9",
            font=("Helvetica", 12)
        )
        self.output_device_label.pack(side=tk.LEFT, padx=10)
        self.output_device_dropdown = ttk.Combobox(
            root,
            textvariable=self.output_device_var,
            font=("Helvetica", 12),
            state="readonly",
            width=50
        )
        self.output_device_dropdown.pack(side=tk.LEFT, padx=10)

        # Populate the dropdowns with audio devices
        self.audio_handler.populate_audio_devices(self.input_device_dropdown, self.output_device_dropdown)