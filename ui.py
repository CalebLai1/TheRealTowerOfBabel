# ui.py

import tkinter as tk
from tkinter import scrolledtext, font, messagebox, ttk
from audio_handler import AudioHandler
from transcription_handler import TranscriptionHandler
from constants import LANGUAGES
import threading
import queue
import numpy as np
import time
import torch

class VoiceTypingAppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Voice Typing")
        self.root.geometry("900x800")  # Increased size to accommodate new buttons
        
        # Initialize Audio and Transcription Handlers BEFORE setting up the UI
        self.audio_handler = AudioHandler()
        self.transcription_handler = TranscriptionHandler()
        
        # Initialize CUDA if available
        self.use_cuda = torch.cuda.is_available()
        if self.use_cuda:
            self.transcription_handler.update_model("base", use_cuda=True)
        
        # Recording state
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.audio_buffer = np.array([], dtype=np.float32)
        
        # Now set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        # Dark theme colors
        self.bg_color = "#2E3440"  # Dark background
        self.fg_color = "#D8DEE9"  # Light text
        self.accent_color = "#5E81AC"  # Accent color for buttons and slider
        self.text_bg_color = "#3B4252"  # Background for text box
        
        # Configure root window background
        self.root.configure(bg=self.bg_color)
        
        # Create a custom font
        self.custom_font = font.Font(family="Helvetica", size=12)
        
        # Create text box with modern styling
        self.text_box = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            width=100, 
            height=30,
            font=self.custom_font,
            bg=self.text_bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,  # Cursor color
            selectbackground=self.accent_color  # Selection color
        )
        self.text_box.pack(padx=20, pady=20, expand=True, fill='both')
        
        # Create control buttons frame
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        # Start/Stop Recording button
        self.record_button = tk.Button(
            button_frame, 
            text="Start Recording",
            command=self.toggle_recording,
            width=15,
            height=2,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.record_button.pack(side=tk.LEFT, padx=10)
        
        # Clear Text button
        self.clear_button = tk.Button(
            button_frame,
            text="Clear Text",
            command=self.clear_text,
            width=15,
            height=2,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)
        
        # Test Audio Input button
        self.test_input_button = tk.Button(
            button_frame,
            text="Test Audio Input",
            command=self.test_audio_input,
            width=15,
            height=2,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.test_input_button.pack(side=tk.LEFT, padx=10)
        
        # Test Audio Output button
        self.test_output_button = tk.Button(
            button_frame,
            text="Test Audio Output",
            command=self.test_audio_output,
            width=15,
            height=2,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.test_output_button.pack(side=tk.LEFT, padx=10)
        
        # Create a frame for the slider and entry widget
        slider_frame = tk.Frame(self.root, bg=self.bg_color)
        slider_frame.pack(pady=10)
        
        # Add a slider for chunk size adjustment
        self.chunk_size_slider = tk.Scale(
            slider_frame,
            from_=0.1,  # Minimum chunk duration (0.1 seconds)
            to=10.0,    # Maximum chunk duration (10 seconds)
            resolution=0.1,  # Allow decimal values
            orient=tk.HORIZONTAL,
            label="Chunk Size (seconds)",
            length=300,
            bg=self.bg_color,
            fg=self.fg_color,
            troughcolor=self.text_bg_color,
            highlightbackground=self.bg_color,
            font=self.custom_font,
            sliderrelief=tk.FLAT,
            activebackground=self.accent_color,
            command=self.update_chunk_size_from_slider
        )
        self.chunk_size_slider.set(3.0)  # Set default value
        self.chunk_size_slider.pack(side=tk.LEFT, padx=10)
        
        # Add an Entry widget for precise input
        self.chunk_size_entry = tk.Entry(
            slider_frame,
            width=5,
            font=self.custom_font,
            bg=self.text_bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.chunk_size_entry.insert(0, "3.0")
        self.chunk_size_entry.pack(side=tk.LEFT, padx=10)
        
        # Add a button to apply the entry value
        self.apply_button = tk.Button(
            slider_frame,
            text="Apply",
            command=self.update_chunk_size_from_entry,
            width=5,
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.custom_font,
            relief=tk.FLAT,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.apply_button.pack(side=tk.LEFT, padx=10)
        
        # Create a frame for audio device selection
        device_frame = tk.Frame(self.root, bg=self.bg_color)
        device_frame.pack(pady=10)
        
        # Add a dropdown for input devices
        self.input_device_var = tk.StringVar()
        self.input_device_label = tk.Label(
            device_frame,
            text="Input Device:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.input_device_label.pack(side=tk.LEFT, padx=10)
        
        self.input_device_dropdown = ttk.Combobox(
            device_frame,
            textvariable=self.input_device_var,
            font=self.custom_font,
            state="readonly",
            width=50
        )
        self.input_device_dropdown.pack(side=tk.LEFT, padx=10)
        
        # Add a dropdown for output devices
        self.output_device_var = tk.StringVar()
        self.output_device_label = tk.Label(
            device_frame,
            text="Output Device:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.output_device_label.pack(side=tk.LEFT, padx=10)
        
        self.output_device_dropdown = ttk.Combobox(
            device_frame,
            textvariable=self.output_device_var,
            font=self.custom_font,
            state="readonly",
            width=50
        )
        self.output_device_dropdown.pack(side=tk.LEFT, padx=10)
        
        # Populate audio device dropdowns
        self.audio_handler.populate_audio_devices(self.input_device_dropdown, self.output_device_dropdown)
        
        # Create a frame for model and language selection
        model_lang_frame = tk.Frame(self.root, bg=self.bg_color)
        model_lang_frame.pack(pady=10)
        
        # Add a dropdown for Whisper model sizes
        self.model_var = tk.StringVar()
        self.model_label = tk.Label(
            model_lang_frame,
            text="Whisper Model:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.model_label.pack(side=tk.LEFT, padx=10)
        
        self.model_dropdown = ttk.Combobox(
            model_lang_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            font=self.custom_font,
            state="readonly",
            width=15
        )
        self.model_dropdown.set("base")  # Set default model
        self.model_dropdown.pack(side=tk.LEFT, padx=10)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.change_model)
        
        # Add a dropdown for language selection
        self.language_var = tk.StringVar()
        self.language_label = tk.Label(
            model_lang_frame,
            text="Language:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font
        )
        self.language_label.pack(side=tk.LEFT, padx=10)
        
        # Populate language dropdown with all supported languages
        self.language_dropdown = ttk.Combobox(
            model_lang_frame,
            textvariable=self.language_var,
            values=list(LANGUAGES.keys()),
            font=self.custom_font,
            state="readonly",
            width=20
        )
        self.language_dropdown.set("English")  # Set default language
        self.language_dropdown.pack(side=tk.LEFT, padx=10)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.change_language)
    
    def update_chunk_size_from_slider(self, value):
        """Update the chunk size based on the slider value."""
        self.chunk_duration = float(value)
        self.chunk_size_entry.delete(0, tk.END)
        self.chunk_size_entry.insert(0, str(self.chunk_duration))
    
    def update_chunk_size_from_entry(self):
        """Update the chunk size based on the entry value."""
        try:
            value = float(self.chunk_size_entry.get())
            if 0.1 <= value <= 10.0:  # Ensure value is within the valid range
                self.chunk_duration = value
                self.chunk_size_slider.set(self.chunk_duration)
            else:
                messagebox.showerror("Invalid Value", "Chunk size must be between 0.1 and 10.0 seconds.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
    
    def clear_text(self):
        """Clear the text box."""
        self.text_box.delete(1.0, tk.END)
    
    def toggle_recording(self):
        """Start or stop recording."""
        if self.is_recording:
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg="#5E81AC")  # Accent color
            self.audio_buffer = np.array([], dtype=np.float32)  # Clear the audio buffer
        else:
            self.is_recording = True
            self.record_button.config(text="Stop Recording", bg="#BF616A")  # Red color for stop
            self.audio_buffer = np.array([], dtype=np.float32)  # Ensure buffer is empty before starting
            self.transcription_handler.update_language(LANGUAGES[self.language_var.get()])
            
            # Start recording and processing threads
            self.recording_thread = threading.Thread(target=self.start_recording, daemon=True)
            self.recording_thread.start()
            
            self.processing_thread = threading.Thread(target=self.process_audio, daemon=True)
            self.processing_thread.start()
    
    def start_recording(self):
        """Start recording audio."""
        selected_input = self.input_device_var.get()
        selected_output = self.output_device_var.get()
        
        if not selected_input:
            messagebox.showerror("Input Device Error", "No input device selected.")
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg=self.accent_color)
            return
        
        # Extract device index from the selected string
        try:
            device_index = int(selected_input.split(']')[0].strip('['))
        except (IndexError, ValueError):
            messagebox.showerror("Device Selection Error", "Invalid input device selection.")
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg=self.accent_color)
            return
        
        # Start the audio stream
        is_recording_flag = threading.Event()
        is_recording_flag.set()
        self.audio_handler.start_recording_stream(
            input_device_index=device_index,
            audio_queue=self.audio_queue,
            is_recording_flag=is_recording_flag
        )
    
    def process_audio(self):
        """Process audio chunks and transcribe them."""
        chunk_duration = self.chunk_size_slider.get()
        chunk_samples = int(self.audio_handler.sample_rate * chunk_duration)
        
        while self.is_recording:
            try:
                if not self.audio_queue.empty():
                    audio_chunk = self.audio_queue.get()
                    self.audio_buffer = np.append(self.audio_buffer, audio_chunk.flatten())
                    
                    # Process when we have enough audio
                    if len(self.audio_buffer) >= chunk_samples:
                        # Transcribe the audio buffer
                        transcription = self.transcription_handler.transcribe_audio_chunk(
                            self.audio_buffer,
                            sample_rate=self.audio_handler.sample_rate,
                            channels=self.audio_handler.channels
                        )
                        
                        # Update text box if transcription is not empty
                        if transcription:
                            self.root.after(0, self.update_text, transcription)
                        
                        # Keep a small overlap for continuous speech
                        overlap_duration = 0.5  # seconds
                        overlap_samples = int(self.audio_handler.sample_rate * overlap_duration)
                        self.audio_buffer = self.audio_buffer[-overlap_samples:]
                else:
                    time.sleep(0.1)  # Prevent busy-waiting
            except Exception as e:
                print(f"Error in processing audio: {e}")
                self.is_recording = False
                self.record_button.config(text="Start Recording", bg="#5E81AC")
                break
    
    def update_text(self, text):
        """Update the text box with transcribed text."""
        if text.strip():
            self.text_box.insert(tk.END, text.strip() + " ")
            self.text_box.see(tk.END)
    
    def test_audio_input(self):
        """Initiate audio input test."""
        selected_input = self.input_device_var.get()
        selected_output = self.output_device_var.get()
        sample_rate = self.audio_handler.sample_rate
        
        if not selected_input or not selected_output:
            messagebox.showerror("Device Selection Error", "Please select both input and output devices for testing.")
            return
        
        # Extract device index from the selected string
        try:
            input_index = int(selected_input.split(']')[0].strip('['))
            output_index = int(selected_output.split(']')[0].strip('['))
        except (IndexError, ValueError):
            messagebox.showerror("Device Selection Error", "Invalid device selection.")
            return
        
        self.audio_handler.test_audio_input(input_device=input_index, output_device=output_index, sample_rate=sample_rate)
    
    def test_audio_output(self):
        """Initiate audio output test."""
        selected_output = self.output_device_var.get()
        sample_rate = self.audio_handler.sample_rate
        
        if not selected_output:
            messagebox.showerror("Output Device Error", "No output device selected.")
            return
        
        # Extract device index from the selected string
        try:
            output_index = int(selected_output.split(']')[0].strip('['))
        except (IndexError, ValueError):
            messagebox.showerror("Device Selection Error", "Invalid output device selection.")
            return
        
        self.audio_handler.test_audio_output(output_device=output_index, sample_rate=sample_rate)
    
    def change_model(self, event):
        """Change the Whisper model based on user selection."""
        selected_model = self.model_var.get()
        self.transcription_handler.update_model(selected_model, use_cuda=self.use_cuda)
    
    def change_language(self, event):
        """Change the transcription language based on user selection."""
        selected_language = self.language_var.get()
        language_code = LANGUAGES[selected_language]
        self.transcription_handler.update_language(language_code)
    
    def run(self):
        """Run the main loop."""
        self.root.mainloop()