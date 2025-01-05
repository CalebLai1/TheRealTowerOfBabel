import gradio as gr
from deep_translator import GoogleTranslator
from elevenlabs.client import ElevenLabs
import speech_recognition as sr
import threading
import tempfile
import os

# Initialize recognizer
recognizer = sr.Recognizer()

# Get all supported languages by Google Translate
SUPPORTED_LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)

# Global variables for recording control
recording_active = False
audio_file_path = None

# Store previous outputs
previous_outputs = []
current_output_index = 0

def save_audio_to_file(audio_data, sample_rate):
    """Save raw audio data to a temporary WAV file."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_data)
        return f.name

def transcribe_and_translate(audio_file, input_lang, output_lang, api_key, voice_id):
    """Transcribe audio, translate text, and generate speech."""
    try:
        # Initialize ElevenLabs client with the provided API key
        client = ElevenLabs(api_key=api_key)

        # Load the audio file
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        # Transcribe audio to text
        text = recognizer.recognize_google(audio, language=input_lang)
        print(f"Transcribed: {text}")

        # Translate text
        translated_text = GoogleTranslator(source=input_lang, target=output_lang).translate(text)
        print(f"Translated: {translated_text}")

        # Generate audio using ElevenLabs
        audio_generator = client.generate(
            text=translated_text,
            voice=voice_id
        )

        # Convert the generator to bytes
        audio_bytes = b"".join(audio_generator)

        # Save the generated audio to a file
        output_file = f"output_{len(previous_outputs)}.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)

        # Store the output
        previous_outputs.append((text, translated_text, output_file))

        return text, translated_text, output_file

    except sr.UnknownValueError:
        return "Could not understand audio", "", None
    except sr.RequestError as e:
        return f"Error: {e}", "", None
    except Exception as e:
        return f"An error occurred: {e}", "", None

def start_recording(audio_length, input_lang, output_lang, api_key, voice_id):
    """Start recording audio for the specified duration and process it."""
    global recording_active, audio_file_path, previous_outputs

    recording_active = True

    while recording_active:
        # Record audio for the specified duration
        with sr.Microphone() as source:
            print(f"Recording for {audio_length} seconds...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source, duration=audio_length)
            print("Recording stopped.")

            # Save the recorded audio to a temporary file
            audio_file_path = save_audio_to_file(audio.get_wav_data(), audio.sample_rate)

        # Process the recorded audio
        transcribed_text, translated_text, output_audio = transcribe_and_translate(
            audio_file_path, input_lang, output_lang, api_key, voice_id
        )

        # Clean up the temporary audio file
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)

        # Yield results to Gradio
        yield transcribed_text, translated_text, output_audio

def stop_recording():
    """Stop recording manually."""
    global recording_active
    recording_active = False
    return "Recording stopped manually.", "", None

def cycle_previous_outputs(direction):
    """Cycle through previous outputs."""
    global current_output_index, previous_outputs

    if not previous_outputs:
        return "No previous outputs", "", None

    if direction == "next":
        current_output_index = (current_output_index + 1) % len(previous_outputs)
    elif direction == "prev":
        current_output_index = (current_output_index - 1) % len(previous_outputs)

    transcribed_text, translated_text, output_audio = previous_outputs[current_output_index]
    return transcribed_text, translated_text, output_audio

# Create Gradio app
with gr.Blocks() as demo:
    gr.Markdown("# Tower of Babel")
    gr.Markdown("**Speak Any Language in Your Own Voice**")

    # Tutorial Section
    with gr.Accordion("📖 **Tutorial: How to Use Tower of Babel**", open=False):
        gr.Markdown("""
        ### Welcome to Tower of Babel!
        Tower of Babel is a revolutionary tool that allows you to:
        - **Speak in your native language** and instantly **translate your words into another language**.
        - **Generate natural-sounding audio** in the translated language using your own voice (via ElevenLabs' voice cloning technology).

        Whether you're a **traveler**, **language enthusiast**, or just curious, Tower of Babel makes communication across languages effortless.

        ### Step-by-Step Guide:
        1. **Set Up Your API Key and Voice ID**:
           - Sign up for an API key from [ElevenLabs](https://elevenlabs.io/).
           - Enter your API key and Voice ID in the respective fields.

        2. **Select Languages**:
           - Choose the **Input Language** (the language you are speaking in).
           - Choose the **Output Language** (the language you want to translate to).

        3. **Set Recording Length**:
           - Use the slider to set the length of each recording (default is 5 seconds).

        4. **Start Recording**:
           - Click the **Start Recording** button to begin recording audio.
           - Speak into your microphone, and the program will:
             - Transcribe your speech into text.
             - Translate the text into the selected output language.
             - Generate audio in the translated language using your voice.

        5. **Stop Recording**:
           - Click the **Stop Recording** button to stop recording manually.

        6. **Cycle Through Previous Outputs**:
           - Use the **Previous Output** and **Next Output** buttons to cycle through previous transcriptions, translations, and generated audio.

        7. **Save and Share**:
           - Download the generated audio files and use them to communicate with others or practice new languages.

        ### Example Workflow:
        1. Select `English` as the input language and `Spanish` as the output language.
        2. Enter your ElevenLabs API key and Voice ID.
        3. Set the recording length to 5 seconds using the slider.
        4. Click **Start Recording**.
        5. Speak into your microphone: "Hello, how are you?"
        6. The program will:
           - Transcribe the audio to text: "Hello, how are you?"
           - Translate the text to Spanish: "Hola, ¿cómo estás?"
           - Generate Spanish audio using your voice.
        7. Use the **Previous Output** and **Next Output** buttons to cycle through previous results.
        8. Click **Stop Recording** to end the process.
        """)

    # Input Section
    with gr.Row():
        input_lang = gr.Dropdown(choices=list(SUPPORTED_LANGUAGES.keys()), label="Input Language", value="en")
        output_lang = gr.Dropdown(choices=list(SUPPORTED_LANGUAGES.keys()), label="Output Language", value="es")
        api_key = gr.Textbox(label="ElevenLabs API Key", placeholder="Enter your API key here")
        voice_id = gr.Textbox(label="ElevenLabs Voice ID", placeholder="Enter your Voice ID here")

    with gr.Row():
        audio_length = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Recording Length (seconds)")

    with gr.Row():
        start_button = gr.Button("Start Recording")
        stop_button = gr.Button("Stop Recording")

    with gr.Row():
        prev_button = gr.Button("Previous Output")
        next_button = gr.Button("Next Output")

    with gr.Row():
        transcribed_text = gr.Textbox(label="Transcribed Text")
        translated_text = gr.Textbox(label="Translated Text")
        output_audio = gr.Audio(label="Generated Audio", type="filepath")

    # Set up button actions
    start_button.click(
        start_recording,
        inputs=[audio_length, input_lang, output_lang, api_key, voice_id],
        outputs=[transcribed_text, translated_text, output_audio]
    )
    stop_button.click(
        stop_recording,
        outputs=[transcribed_text, translated_text, output_audio]
    )
    prev_button.click(
        cycle_previous_outputs,
        inputs=gr.Textbox("prev", visible=False),
        outputs=[transcribed_text, translated_text, output_audio]
    )
    next_button.click(
        cycle_previous_outputs,
        inputs=gr.Textbox("next", visible=False),
        outputs=[transcribed_text, translated_text, output_audio]
    )

# Launch the app
demo.launch()