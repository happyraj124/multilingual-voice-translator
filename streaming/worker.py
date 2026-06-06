import queue
import threading
import numpy as np
import time
from tts.mms_tts import speak


class STTWorker(threading.Thread):

    def __init__(
        self,
        whisper_model,
        speech_queue
    ):

        super().__init__(daemon=True)

        self.whisper_model = whisper_model

        self.speech_queue = speech_queue

        self.text_queue = queue.Queue()

        self.display_queue = queue.Queue()

        self.running = True

    def run(self):

        print("STT Worker Started")

        while self.running:

            segment = self.speech_queue.get()

            try:

                audio = segment.astype(
                    np.float32
                )

                result = (
                    self.whisper_model.transcribe(
                        audio,
                        fp16=False
                    )
                )

                text = (
                    result["text"]
                    .strip()
                )

                if text:

                    print(
                        f"STT: {text}"
                    )

                    self.text_queue.put(
                        text
                    )
                    self.display_queue.put(
                        text
                    )

            except Exception as e:

                print(
                    "STT Error:",
                    e
                )

    def stop(self):

        self.running = False


class TranslationWorker(threading.Thread):

    def __init__(
        self,
        translator_model,
        tokenizer,
        text_queue,
        target_language
    ):

        super().__init__(daemon=True)

        self.translator_model = translator_model

        self.tokenizer = tokenizer

        self.text_queue = text_queue

        self.target_language = target_language

        self.translation_queue = queue.Queue()

        self.display_queue = queue.Queue()

        self.running = True

    def run(self):

        print(
            "Translation Worker Started"
        )

        while self.running:

            text = self.text_queue.get()

            try:

                inputs = self.tokenizer(
                    text,
                    return_tensors="pt"
                )

                translated_tokens = (
                    self.translator_model.generate(
                        **inputs,
                        forced_bos_token_id=
                        self.tokenizer.convert_tokens_to_ids(
                            self.target_language
                        ),
                        max_length=256
                    )
                )

                translated_text = (
                    self.tokenizer.batch_decode(
                        translated_tokens,
                        skip_special_tokens=True
                    )[0]
                )

                print(
                    f"Translation: "
                    f"{translated_text}"
                )

                self.translation_queue.put(
                    translated_text
                )
                self.display_queue.put(
                    translated_text
                )

            except Exception as e:

                print(
                    "Translation Error:",
                    e
                )

    def stop(self):

        self.running = False


class TTSWorker(threading.Thread):

    def __init__(
        self,
        translation_queue,
        target_language
    ):

        super().__init__(daemon=True)

        self.translation_queue = translation_queue

        self.target_language = target_language

        self.running = True

        self.is_speaking = False

        self.last_tts_time = 0

    def run(self):

        print(
            "TTS Worker Started"
        )

        while self.running:

            translated_text = (
                self.translation_queue.get()
            )

            try:

                self.is_speaking = True

                print(
                    f"TTS: {translated_text}"
                )

                speak(
                    translated_text,
                    self.target_language
                )

                self.last_tts_time = (
                    time.time()
                )

                self.is_speaking = False

            except Exception as e:

                self.is_speaking = False

                print(
                    "TTS Error:",
                    e
                )

    def stop(self):

        self.running = False