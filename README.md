# Tower of Babel - Real-time Voice Translation

This project provides a real-time voice-to-text transcription and translation tool using the Vosk and Whisper models. It also integrates with ElevenLabs for text-to-speech functionality, allowing you to translate spoken language into another language and generate audio output.

## Features

- **Real-time Transcription**: Transcribe spoken language in real-time using the Vosk model.
- **Whisper Transcription**: Transcribe pre-recorded audio files using the Whisper model.
- **Translation**: Translate transcribed text into multiple languages using Google Translate.
- **Text-to-Speech**: Generate audio output from translated text using ElevenLabs.
- **Audio Playback**: Play recorded or generated audio files sequentially or individually.
- **Microphone Test**: Record and playback audio to test your microphone.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/CalebLai1/TheRealTowerOfBabel.git
   cd tower-of-babel
Install the required dependencies:

bash
Copy
pip install -r requirements.txt
Download the necessary Vosk models. The application will prompt you to download the models when you select a language and model size.

Usage
Run the application:

bash
Copy
python main.py
Use the GUI to:

Select the language and model size for transcription.

Start and stop real-time transcription.

Upload or record audio files for Whisper transcription.

Translate transcribed text into your desired language.

Generate and play audio output using ElevenLabs.

Requirements
Python 3.8 or higher

See requirements.txt for a list of dependencies.