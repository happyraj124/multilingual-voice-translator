"""
models/model_manager.py
"""

import whisper
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tts.mms_tts import load_model


class ModelManager:

    def __init__(self):
        self.whisper_model    = None
        self.translator_model = None
        self.tokenizer        = None

    def load_models(self) -> None:
        print("\nLoading Whisper Model...")
        self.whisper_model = whisper.load_model("medium")
        print("Whisper Loaded!")

        model_name = "facebook/nllb-200-distilled-600M"
        print("\nLoading Translator...")
        self.tokenizer        = AutoTokenizer.from_pretrained(model_name)
        self.translator_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print("Translator Loaded!")

        print("\nPreloading MMS TTS Models...")
        for lang in ["eng_Latn", "hin_Deva"]:
            try:
                load_model(lang)
                print(f"  ✓ MMS loaded: {lang}")
            except Exception as e:
                print(f"  ✗ MMS failed: {lang} — {e}")

        print("MMS Preloading Complete!")
