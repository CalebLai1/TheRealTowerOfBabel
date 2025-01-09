# model_handler.py
import os
import threading
import requests
import zipfile
import io
import time
from tkinter import messagebox
from vosk import Model, KaldiRecognizer
from utils import show_progress_bar, hide_progress_bar, update_progress_bar
from model import voskModels

class ModelHandler:
    def __init__(self, gui):
        self.gui = gui
        self.vosk_models = voskModels
        self.model = None
        self.recognizer = None
        self.download_thread = None
        self.stop_event = threading.Event()

    def load_model(self):
        language = self.gui.language_var.get()
        size = self.gui.size_var.get()
        model_info = self.vosk_models.get(language, {}).get(size)

        if not model_info:
            messagebox.showerror("Error", f"Model for {language} ({size}) not found in voskModels.")
            return False

        model_name = model_info['name']
        model_url = model_info['url']
        model_path = os.path.join("models", model_name)

        if not os.path.exists(model_path):
            response = messagebox.askyesno(
                "Model Not Found",
                f"The selected model '{model_name}' is not found in the 'models' folder.\nDo you want to download it now?"
            )
            if response:
                self.download_thread = threading.Thread(target=self.download_and_extract_model, args=(model_url, model_name))
                self.download_thread.start()
                self.gui.root.after(100, self.check_download_thread)
            else:
                return False
        else:
            self.initialize_model(model_path)

    def check_download_thread(self):
        if self.download_thread.is_alive():
            self.gui.root.after(100, self.check_download_thread)
        else:
            if self.initialize_model(os.path.join("models", self.vosk_models[self.gui.language_var.get()][self.gui.size_var.get()]['name'])):
                messagebox.showinfo("Success", "Model downloaded and loaded successfully.")
            else:
                messagebox.showerror("Error", "Failed to load the model after downloading.")

    def download_and_extract_model(self, url, model_name):
        try:
            self.gui.show_progress_bar()
            response = requests.get(url, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:
                self.gui.hide_progress_bar()
                messagebox.showerror("Error", "Failed to retrieve the model. No content-length header.")
                return

            total_length = int(total_length)
            downloaded = 0
            chunk_size = 1024 * 1024  # 1 MB
            zip_content = io.BytesIO()

            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    zip_content.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / total_length) * 100
                    self.gui.update_progress_bar(percent)

            with zipfile.ZipFile(zip_content) as zip_ref:
                zip_ref.extractall(os.path.join("models"))

            self.gui.update_progress_bar(100)
            time.sleep(0.5)
            self.gui.hide_progress_bar()
        except Exception as e:
            self.gui.hide_progress_bar()
            messagebox.showerror("Download Error", f"An error occurred while downloading the model: {e}")

    def initialize_model(self, model_path):
        try:
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            messagebox.showinfo("Success", "Model loaded successfully.")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {e}")
            return False
