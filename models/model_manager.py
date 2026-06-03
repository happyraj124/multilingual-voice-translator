import whisper

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


class ModelManager:

    def __init__(self):

        self.whisper_model = None

        self.translator_model = None

        self.tokenizer = None

    def load_models(self):

        print("\nLoading Whisper Model...")

        self.whisper_model = whisper.load_model(
            "medium"
        )

        print("Whisper Loaded!")

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