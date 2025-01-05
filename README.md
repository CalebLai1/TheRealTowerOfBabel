Tower of Babel
Speak Any Language in Your Own Voice

Tower of Babel is a revolutionary tool that allows you to speak in your native language and instantly translate your words into another language. Using ElevenLabs' voice cloning technology, you can generate natural-sounding audio in the translated language using your own voice. Whether you're a traveler, language enthusiast, or just curious, Tower of Babel makes communication across languages effortless.

Features
Real-Time Transcription: Speak into your microphone, and the app will transcribe your speech into text.

Instant Translation: Translate the transcribed text into your desired language.

Voice Cloning: Generate natural-sounding audio in the translated language using your own voice (via ElevenLabs' voice cloning technology).

Cycle Through Outputs: Easily review previous transcriptions, translations, and generated audio.

User-Friendly Interface: Built with Gradio for an intuitive and interactive experience.

Getting Started
Prerequisites
Python 3.7+: Ensure you have Python installed on your system.

ElevenLabs API Key: Sign up for an API key from ElevenLabs.

Voice ID: Obtain your Voice ID from ElevenLabs for voice cloning.

Installation
Clone the repository:

bash
Copy
git clone https://github.com/CalebLai1/TheRealTowerOfBabel.git
cd tower-of-babel
Install the required dependencies:

bash
Copy
pip install -r requirements.txt
Run the app:

bash
Copy
python app.py
Open your browser and navigate to the Gradio interface (usually at http://127.0.0.1:7860).

How to Use
Step-by-Step Guide
Set Up Your API Key and Voice ID:

Enter your ElevenLabs API key and Voice ID in the respective fields.

Select Languages:

Choose the Input Language (the language you are speaking in).

Choose the Output Language (the language you want to translate to).

Set Recording Length:

Use the slider to set the length of each recording (default is 5 seconds).

Start Recording:

Click the Start Recording button to begin recording audio.

Speak into your microphone, and the program will:

Transcribe your speech into text.

Translate the text into the selected output language.

Generate audio in the translated language using your voice.

Stop Recording:

Click the Stop Recording button to stop recording manually.

Cycle Through Previous Outputs:

Use the Previous Output and Next Output buttons to cycle through previous transcriptions, translations, and generated audio.

Save and Share:

Download the generated audio files and use them to communicate with others or practice new languages.

Example Workflow
Select English as the input language and Spanish as the output language.

Enter your ElevenLabs API key and Voice ID.

Set the recording length to 5 seconds using the slider.

Click Start Recording.

Speak into your microphone: "Hello, how are you?"

The program will:

Transcribe the audio to text: "Hello, how are you?"

Translate the text to Spanish: "Hola, ¿cómo estás?"

Generate Spanish audio using your voice.

Use the Previous Output and Next Output buttons to cycle through previous results.

Click Stop Recording to end the process.

Requirements
gradio

deep-translator

elevenlabs

speechrecognition

numpy

scipy

Install all dependencies using:

bash
Copy
pip install gradio deep-translator elevenlabs speechrecognition numpy scipy
Contributing
Contributions are welcome! If you'd like to contribute to Tower of Babel, please follow these steps:

Fork the repository.

Create a new branch (git checkout -b feature/YourFeatureName).

Commit your changes (git commit -m 'Add some feature').

Push to the branch (git push origin feature/YourFeatureName).

Open a pull request.

Acknowledgments
ElevenLabs: For their state-of-the-art voice cloning technology.

Google Translate: For providing the translation API.

Gradio: For making it easy to build interactive web interfaces.

Start using Tower of Babel today and speak any language in your own voice!
