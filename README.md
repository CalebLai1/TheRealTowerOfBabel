# Tower of Babel - Speak Any Language in Your Own Voice

Tower of Babel is a revolutionary tool that allows you to speak in your native language and instantly translate your words into another language. Using state-of-the-art transcription, translation, and ElevenLabs' voice cloning technology, you can generate natural-sounding audio in the translated language using your own voice. Whether you're a traveler, language enthusiast, or just curious, Tower of Babel makes communication across languages effortless.

## Features

- **Real-Time Transcription**: Transcribe spoken language in real-time using the Vosk model.
- **Whisper Transcription**: Transcribe pre-recorded audio files using the Whisper model.
- **Instant Translation**: Translate transcribed text into multiple languages using Google Translate.
- **Voice Cloning**: Generate natural-sounding audio in the translated language using your own voice (via ElevenLabs' voice cloning technology).
- **Audio Playback**: Play recorded or generated audio files sequentially or individually.
- **Cycle Through Outputs**: Easily review previous transcriptions, translations, and generated audio.
- **Microphone Test**: Record and playback audio to test your microphone.
- **User-Friendly Interface**: Built with Gradio for an intuitive and interactive experience.

---

## Getting Started

### Prerequisites

- **Python 3.8 or higher**: Ensure Python is installed on your system.
- **ElevenLabs API Key**: Sign up for an API key from ElevenLabs.
- **Voice ID**: Obtain your Voice ID from ElevenLabs for voice cloning.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/CalebLai1/TheRealTowerOfBabel.git
   cd tower-of-babel
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download the necessary Vosk models. The application will prompt you to download the models when you select a language and model size.

---

## How to Use

### Step-by-Step Guide

1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Set Up Your API Key and Voice ID**:
   - Enter your ElevenLabs API key and Voice ID in the respective fields.

3. **Select Languages**:
   - Choose the **Input Language** (the language you are speaking in).
   - Choose the **Output Language** (the language you want to translate to).

4. **Set Recording Length**:
   - Use the slider to set the length of each recording (default is 5 seconds).

5. **Start Recording**:
   - Click the **Start Recording** button to begin recording audio.
   - Speak into your microphone, and the program will:
     - Transcribe your speech into text.
     - Translate the text into the selected output language.
     - Generate audio in the translated language using your voice.

6. **Stop Recording**:
   - Click the **Stop Recording** button to stop recording manually.

7. **Cycle Through Outputs**:
   - Use the **Previous Output** and **Next Output** buttons to review previous transcriptions, translations, and generated audio.

8. **Save and Share**:
   - Download the generated audio files to communicate with others or practice new languages.

---

## Example Workflow

1. Select **English** as the input language and **Spanish** as the output language.
2. Enter your ElevenLabs API key and Voice ID.
3. Set the recording length to 5 seconds using the slider.
4. Click **Start Recording** and speak into your microphone: *"Hello, how are you?"*
   - The program will:
     - Transcribe the audio to text: *"Hello, how are you?"*
     - Translate the text to Spanish: *"Hola, ¿como estás?"*
     - Generate Spanish audio using your voice.
5. Use the **Previous Output** and **Next Output** buttons to cycle through results.
6. Click **Stop Recording** to end the process.

---

## Requirements

- `gradio`
- `deep-translator`
- `elevenlabs`
- `speechrecognition`
- `numpy`
- `scipy`

Install all dependencies using:
```bash
pip install gradio deep-translator elevenlabs speechrecognition numpy scipy
```

---

## Contributing

Contributions are welcome! If you'd like to contribute to Tower of Babel, please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a pull request.

---

## Acknowledgments

- **ElevenLabs**: For their state-of-the-art voice cloning technology.
- **Google Translate**: For providing the translation API.
- **Gradio**: For making it easy to build interactive web interfaces.
- **Vosk and Whisper Models**: For robust and accurate transcription capabilities.

---

Start using Tower of Babel today and break the barriers of language!

