# Voice-to-Voice Translation Tool

This project is a voice-to-voice translation tool that transcribes recorded audio, translates it into selected languages, and generates audio for the translated text. It leverages OpenAI's Whisper model for transcription, Google Translate for translation, and ElevenLabs for text-to-speech (TTS). The user interface is built with Gradio, providing an intuitive way to upload, translate, and listen to audio in multiple languages.

## Features
- **Speech Transcription**: Converts audio input to text using OpenAI’s Whisper.
- **Multi-language Translation**: Translates transcriptions into multiple target languages using Google Translate.
- **Text-to-Speech (TTS)**: Generates audio for each translated text using ElevenLabs.
- **Dynamic Language Support**: Retrieves supported languages from Google Translate, ensuring broad language compatibility.

## Requirements

To install the required packages, use the following command:

```bash
pip install -r requirements.txt
