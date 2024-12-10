import uuid
from pathlib import Path
from pydub import AudioSegment
import whisper
import gradio as gr
from deep_translator import GoogleTranslator
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv()

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

model = whisper.load_model("small")

TARGET_LANGUAGES = {
    "Afrikaans": "af",
    "Albanian": "sq",
    "Amharic": "am",
    "Arabic": "ar",
    "Armenian": "hy",
    "Azerbaijani": "az",
    "Basque": "eu",
    "Belarusian": "be",
    "Bengali": "bn",
    "Bosnian": "bs",
    "Bulgarian": "bg",
    "Catalan": "ca",
    "Cebuano": "ceb",
    "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "Corsican": "co",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Esperanto": "eo",
    "Estonian": "et",
    "Finnish": "fi",
    "French": "fr",
    "Frisian": "fy",
    "Galician": "gl",
    "Georgian": "ka",
    "Greek": "el",
    "Gujarati": "gu",
    "Haitian Creole": "ht",
    "Hausa": "ha",
    "Hawaiian": "haw",
    "Hebrew": "he",
    "Hindi": "hi",
    "Hmong": "hmn",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Igbo": "ig",
    "Indonesian": "id",
    "Irish": "ga",
    "Italian": "it",
    "Javanese": "jv",
    "Kannada": "kn",
    "Kazakh": "kk",
    "Khmer": "km",
    "Kinyarwanda": "rw",
    "Korean": "ko",
    "Kurdish (Kurmanji)": "ku",
    "Kyrgyz": "ky",
    "Lao": "lo",
    "Latin": "la",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Luxembourgish": "lb",
    "Macedonian": "mk",
    "Malagasy": "mg",
    "Malay": "ms",
    "Malayalam": "ml",
    "Maltese": "mt",
    "Maori": "mi",
    "Marathi": "mr",
    "Mongolian": "mn",
    "Myanmar (Burmese)": "my",
    "Nepali": "ne",
    "Norwegian": "no",
    "Nyanja (Chichewa)": "ny",
    "Odia (Oriya)": "or",
    "Pashto": "ps",
    "Persian": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Punjabi": "pa",
    "Romanian": "ro",
    "Russian": "ru",
    "Samoan": "sm",
    "Scots Gaelic": "gd",
    "Serbian": "sr",
    "Sesotho": "st",
    "Shona": "sn",
    "Sindhi": "sd",
    "Sinhala (Sinhalese)": "si",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Somali": "so",
    "Spanish": "es",
    "Sundanese": "su",
    "Swahili": "sw",
    "Swedish": "sv",
    "Tagalog (Filipino)": "tl",
    "Tajik": "tg",
    "Tamil": "ta",
    "Tatar": "tt",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Turkmen": "tk",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Uyghur": "ug",
    "Uzbek": "uz",
    "Vietnamese": "vi",
    "Welsh": "cy",
    "Xhosa": "xh",
    "Yiddish": "yi",
    "Yoruba": "yo",
    "Zulu": "zu"
}

history_1 = {"translations": [], "audio_files": []}
history_2 = {"translations": [], "audio_files": []}

def transcribe_audio(audio_file):
    wav_file = convert_to_wav(audio_file)
    result = model.transcribe(str(wav_file))
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

def translate_text(text: str, target_lang: str) -> str:
    translator = GoogleTranslator(source='auto', target=target_lang)
    translation = translator.translate(text)
    return translation

def text_to_speech(text: str, api_key: str, voice_id: str) -> str:
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
    return str(save_file_path)

def save_to_history(history, translation, audio_file):
    history["translations"].append(translation)
    history["audio_files"].append(audio_file)

def process_input(audio_file, input_text):
    if input_text and input_text.strip():
        return input_text.strip()
    elif audio_file:
        return transcribe_audio(audio_file)
    else:
        return "No input provided."

def voice_to_voice_with_history(audio_file, input_text, 
                                person_input_lang, other_person_input_lang,
                                history, api_key, voice_id):
    # person_input_lang is the language name chosen by the speaker
    # other_person_input_lang is the language name of the other speaker
    # We'll translate from the speaker's input language to the other speaker's input language.
    if other_person_input_lang not in TARGET_LANGUAGES or person_input_lang not in TARGET_LANGUAGES:
        return None, "Translation Error: Unsupported language."

    final_input_text = process_input(audio_file, input_text)
    if final_input_text == "No input provided.":
        return None, "No input provided."

    target_lang_code = TARGET_LANGUAGES.get(other_person_input_lang)  # Translate into the other speaker's language
    translation = translate_text(final_input_text, target_lang_code)
    translated_audio_file_name = text_to_speech(translation, api_key, voice_id) if "Translation Error" not in translation else None
    save_to_history(history, translation, translated_audio_file_name)
    return translated_audio_file_name, translation

def get_previous_translation(history, index):
    if 0 <= index < len(history["translations"]):
        return history["translations"][index]
    return "No previous translation available."

def get_previous_audio(history, index):
    if 0 <= index < len(history["audio_files"]):
        return history["audio_files"][index]
    return None

with gr.Blocks() as demo:
    gr.Markdown("# Welcome To The Tower of Babel")

    with gr.Row():
        # Left Column: Instructions and Credentials
        with gr.Column():
            with gr.Group():
                gr.Markdown("""
                **How it Works Now**:
                - Person 1 selects their input language.
                - Person 2 selects their input language.
                
                When Person 1 speaks/types, it will be translated into Person 2's chosen language.  
                When Person 2 speaks/types, it will be translated into Person 1's chosen language.
                
                **Note**:  
                - Enter your Eleven Labs API Key and Voice IDs below.  
                - In the middle column (Person 1) and right column (Person 2):
                  - You can record audio OR type text directly.
                  - No need to choose a target language each time; the output language is always the other's input language.
                """)

            with gr.Group():
                gr.Markdown("### Enter Your Eleven Labs Credentials")
                api_key_input = gr.Textbox(label="API Key", type="password")
                voice_id_input_1 = gr.Textbox(label="Voice ID (Person 1)")
                voice_id_input_2 = gr.Textbox(label="Voice ID (Person 2)")

        # Middle Column: Person 1
        with gr.Column():
            gr.Markdown("## Person 1")
            person1_input_language = gr.Dropdown(choices=list(TARGET_LANGUAGES.keys()), label="Person 1's Input Language")
            audio_input_1 = gr.Audio(sources=["microphone"], type="filepath", show_download_button=True, label="Record Audio (optional)")
            text_input_1 = gr.Textbox(label="Or type your text here (Person 1)")

            submit_1 = gr.Button("Submit", variant="primary")
            audio_output_1 = gr.Audio(label="Translated Audio", interactive=False)
            text_output_1 = gr.Markdown()
            prev_translation_1 = gr.Markdown()
            prev_button_1 = gr.Button("Previous Translation")
            next_button_1 = gr.Button("Next Translation")
            history_index_1 = gr.State(value=0)

        # Right Column: Person 2
        with gr.Column():
            gr.Markdown("## Person 2")
            person2_input_language = gr.Dropdown(choices=list(TARGET_LANGUAGES.keys()), label="Person 2's Input Language")
            audio_input_2 = gr.Audio(sources=["microphone"], type="filepath", show_download_button=True, label="Record Audio (optional)")
            text_input_2 = gr.Textbox(label="Or type your text here (Person 2)")

            submit_2 = gr.Button("Submit", variant="primary")
            audio_output_2 = gr.Audio(label="Translated Audio", interactive=False)
            text_output_2 = gr.Markdown()
            prev_translation_2 = gr.Markdown()
            prev_button_2 = gr.Button("Previous Translation")
            next_button_2 = gr.Button("Next Translation")
            history_index_2 = gr.State(value=0)

    # Person 1 submission: translate from Person 1's input lang to Person 2's input lang
    submit_1.click(
        fn=lambda audio_file, input_text, p1_lang, p2_lang, api_key, voice_id: voice_to_voice_with_history(
            audio_file, input_text, p1_lang, p2_lang, history_1, api_key, voice_id
        ),
        inputs=[audio_input_1, text_input_1, person1_input_language, person2_input_language, api_key_input, voice_id_input_1],
        outputs=[audio_output_1, text_output_1]
    )

    prev_button_1.click(
        fn=lambda index: (
            max(0, index - 1),
            get_previous_translation(history_1, max(0, index - 1)),
            get_previous_audio(history_1, max(0, index - 1)),
        ),
        inputs=[history_index_1],
        outputs=[history_index_1, prev_translation_1, audio_output_1]
    )

    next_button_1.click(
        fn=lambda index: (
            min(len(history_1["translations"]) - 1, index + 1),
            get_previous_translation(history_1, min(len(history_1["translations"]) - 1, index + 1)),
            get_previous_audio(history_1, min(len(history_1["translations"]) - 1, index + 1)),
        ),
        inputs=[history_index_1],
        outputs=[history_index_1, prev_translation_1, audio_output_1]
    )

    # Person 2 submission: translate from Person 2's input lang to Person 1's input lang
    submit_2.click(
        fn=lambda audio_file, input_text, p2_lang, p1_lang, api_key, voice_id: voice_to_voice_with_history(
            audio_file, input_text, p2_lang, p1_lang, history_2, api_key, voice_id
        ),
        inputs=[audio_input_2, text_input_2, person2_input_language, person1_input_language, api_key_input, voice_id_input_2],
        outputs=[audio_output_2, text_output_2]
    )

    prev_button_2.click(
        fn=lambda index: (
            max(0, index - 1),
            get_previous_translation(history_2, max(0, index - 1)),
            get_previous_audio(history_2, max(0, index - 1)),
        ),
        inputs=[history_index_2],
        outputs=[history_index_2, prev_translation_2, audio_output_2]
    )

    next_button_2.click(
        fn=lambda index: (
            min(len(history_2["translations"]) - 1, index + 1),
            get_previous_translation(history_2, min(len(history_2["translations"]) - 1, index + 1)),
            get_previous_audio(history_2, min(len(history_2["translations"]) - 1, index + 1)),
        ),
        inputs=[history_index_2],
        outputs=[history_index_2, prev_translation_2, audio_output_2]
    )

if __name__ == "__main__":
    demo.launch()
