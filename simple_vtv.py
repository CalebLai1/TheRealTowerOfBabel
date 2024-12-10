import os
import uuid
from pathlib import Path
from pydub import AudioSegment
import whisper
import gradio as gr
from deep_translator import GoogleTranslator
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Define directories for input and output audio
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load Whisper model for transcription
model = whisper.load_model("small")  # Options: "tiny", "base", "small", "medium", "large"

# Retrieve supported languages
supported_languages = GoogleTranslator.get_supported_languages(as_dict=True)
language_name_to_code = {name: code for code, name in supported_languages.items()}
sorted_languages = sorted(language_name_to_code.items(), key=lambda x: x[0])

def voice_to_voice(audio_file, selected_languages, api_key, voice_id_1, voice_id_2):
    """
    Transcribe the input audio, translate the text into selected languages,
    convert the translations to speech, and return the audio players.

    Note: Currently, this function only uses voice_id_1 for demonstration.
    You can adapt the code to use voice_id_2 depending on your use case.
    """
    try:
        if not api_key or not voice_id_1:
            raise gr.Error("Please provide your Eleven Labs API key and at least the first Voice ID.")

        # Save the original audio to the input directory
        input_audio_path = save_input_audio(audio_file)
        
        # Transcribe audio using Whisper
        transcript = transcribe_audio(input_audio_path)
        
        if not selected_languages:
            raise gr.Error("Please select at least one target language for translation.")
        
        # Translate the transcribed text
        list_translations = translate_text(transcript, selected_languages)
        
        # Generate speech from translated text (using voice_id_1 by default)
        generated_audio_paths = []
        for translation in list_translations:
            if "Translation Error" in translation:
                generated_audio_paths.append(None)
            else:
                # Use voice_id_1. You could decide based on language or user input which voice ID to use.
                translated_audio_file_name = text_to_speech(translation, api_key, voice_id_1)
                audio_path = Path(translated_audio_file_name)
                generated_audio_paths.append(audio_path)
        
        # Generate HTML with audio players for each translated language
        html_output = generate_html_output(generated_audio_paths, selected_languages)
        
        return html_output

    except gr.Error as e:
        return f"<p style='color:red;'>{str(e)}</p>"
    except Exception as e:
        return f"<p style='color:red;'>Unexpected Error: {str(e)}</p>"

def save_input_audio(audio_file):
    original_extension = Path(audio_file).suffix
    unique_filename = f"{uuid.uuid4()}{original_extension}"
    input_path = INPUT_DIR / unique_filename
    os.rename(audio_file, input_path)
    return input_path

def transcribe_audio(audio_path):
    wav_file = convert_to_wav(audio_path)
    result = model.transcribe(wav_file)
    transcription_text = result["text"].strip()
    os.remove(wav_file)
    return transcription_text

def convert_to_wav(audio_path):
    audio = AudioSegment.from_file(audio_path)
    wav_filename = f"{uuid.uuid4()}.wav"
    wav_path = INPUT_DIR / wav_filename
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(wav_path, format="wav")
    return wav_path

def translate_text(text, selected_languages):
    list_translations = []
    for lang in selected_languages:
        lang_code = language_name_to_code.get(lang)
        if not lang_code:
            list_translations.append(f"Translation Error: Unsupported language '{lang}'.")
            continue
        try:
            translator = GoogleTranslator(source="auto", target=lang_code)
            translation = translator.translate(text)
            list_translations.append(translation)
        except Exception as e:
            list_translations.append(f"Translation Error: {str(e)}")
    return list_translations

def text_to_speech(text, api_key, voice_id):
    try:
        client = ElevenLabs(api_key=api_key)
        response = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.8,
                style=0.5,
                use_speaker_boost=True,
            ),
        )
        save_file_path = OUTPUT_DIR / f"{uuid.uuid4()}.mp3"
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        return save_file_path
    except Exception as e:
        raise gr.Error(f"TTS Error: {str(e)}")

def generate_html_output(audio_paths, languages):
    html = ""
    for audio_path, lang in zip(audio_paths, languages):
        if audio_path:
            relative_path = os.path.relpath(audio_path, start=OUTPUT_DIR.parent)
            html += f"""
            <div style="margin-bottom: 20px;">
                <h3>{lang}</h3>
                <audio controls>
                    <source src="{relative_path}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            </div>
            """
        else:
            html += f"""
            <div style="margin-bottom: 20px;">
                <h3>{lang}</h3>
                <p style='color:red;'>Audio generation failed for this language.</p>
            </div>
            """
    return html

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("## Voice-to-Voice Translator with Dynamic API Key and Two Voice IDs")

    api_key_input = gr.Textbox(label="Enter your Eleven Labs API Key", type="password")
    voice_id_input_1 = gr.Textbox(label="Enter your Voice ID for Person 1")
    voice_id_input_2 = gr.Textbox(label="Enter your Voice ID for Person 2")

    with gr.Row():
        audio_input = gr.Audio(source="microphone", type="filepath", label="Input Audio")
        language_selection = gr.CheckboxGroup(
            choices=[lang for lang, code in sorted_languages],
            label="Select Target Languages",
        )
        submit_button = gr.Button("Translate")

    output_section = gr.HTML(label="Translated Audio")

    # For now, we just pass both voice IDs, but only use voice_id_1 in code above.
    submit_button.click(
        fn=voice_to_voice,
        inputs=[audio_input, language_selection, api_key_input, voice_id_input_1, voice_id_input_2],
        outputs=output_section
    )

if __name__ == "__main__":
    demo.launch()
