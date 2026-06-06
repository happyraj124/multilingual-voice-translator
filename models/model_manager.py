import whisper

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)

from tts.mms_tts import load_model


class ModelManager:

    def __init__(self):

        self.whisper_model = None

        self.translator_model = None

        self.tokenizer = None

    def load_models(self):

        # ==========================
        # Whisper
        # ==========================

        print("\nLoading Whisper Model...")

        self.whisper_model = whisper.load_model(
            "medium"
        )

        print("Whisper Loaded!")

        # ==========================
        # Translator
        # ==========================

        model_name = (
            "facebook/nllb-200-distilled-600M"
        )

        print("\nLoading Translator...")

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                model_name
            )
        )

        self.translator_model = (
            AutoModelForSeq2SeqLM
            .from_pretrained(model_name)
        )

        print("Translator Loaded!")

        # ==========================
        # MMS-TTS Preloading
        # ==========================

        print("\nPreloading MMS Models...")

        preload_languages = [

            "eng_Latn",
            "hin_Deva"

        ]

        for language in preload_languages:

            try:

                load_model(language)

                print(
                    f"Loaded MMS: {language}"
                )

            except Exception as e:

                print(
                    f"Failed MMS: {language}"
                )

                print(e)

        print("MMS Preloading Complete!")