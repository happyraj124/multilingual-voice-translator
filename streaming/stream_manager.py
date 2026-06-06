import queue
import time

from streaming.audio_stream import AudioStream
from streaming.vad_detector import VADDetector

from streaming.worker import (
    STTWorker,
    TranslationWorker,
    TTSWorker
)


class StreamManager:

    def __init__(
        self,
        model_manager,
        target_language
    ):

        self.model_manager = model_manager

        self.target_language = (
            target_language
        )

        self.stream = None

        self.vad = None

        self.stt_worker = None

        self.translation_worker = None

        self.tts_worker = None

        self.running = False

        self.transcript_queue = (
            queue.Queue()
        )

        self.translation_display_queue = (
            queue.Queue()
        )

    def start_streaming(self):

        if self.running:
            return

        self.stream = AudioStream()

        self.vad = VADDetector(
            silence_duration=1.5,
            speech_threshold=0.01,
            min_speech_duration=0.8
        )

        self.stt_worker = STTWorker(
            self.model_manager.whisper_model,
            self.vad.speech_queue
        )

        self.translation_worker = (
            TranslationWorker(
                self.model_manager.translator_model,
                self.model_manager.tokenizer,
                self.stt_worker.text_queue,
                self.target_language
            )
        )

        self.tts_worker = TTSWorker(
            self.translation_worker.translation_queue,
            self.target_language
        )

        self.transcript_queue = (
            self.stt_worker.display_queue
        )

        self.translation_display_queue = (
            self.translation_worker.display_queue
        )

        self.stt_worker.start()

        self.translation_worker.start()

        self.tts_worker.start()

        self.stream.start()

        self.running = True

    def process(self):

        if not self.running:
            return

        chunk = self.stream.get_chunk()

        if (
            not self.tts_worker.is_speaking
            and
            time.time()
            - self.tts_worker.last_tts_time
            > 1
        ):

            self.vad.process_chunk(
                chunk
            )

    def stop_streaming(self):

        if not self.running:
            return

        self.stt_worker.stop()

        self.translation_worker.stop()

        self.tts_worker.stop()

        self.stream.stop()

        self.running = False