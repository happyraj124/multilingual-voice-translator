from models.model_manager import (
    ModelManager
)

from streaming.audio_stream import (
    AudioStream
)

from streaming.vad_detector import (
    VADDetector
)

from streaming.worker import (
    STTWorker,
    TranslationWorker,
    TTSWorker
)


def main():

    manager = ModelManager()

    manager.load_models()

    target_language = "hin_Deva"

    stream = AudioStream()

    vad = VADDetector(
        silence_duration=1.5,
        speech_threshold=0.01,
        min_speech_duration=0.8
    )

    stt_worker = STTWorker(
        manager.whisper_model,
        vad.speech_queue
    )

    translation_worker = TranslationWorker(
        manager.translator_model,
        manager.tokenizer,
        stt_worker.text_queue,
        target_language
    )

    tts_worker = TTSWorker(
        translation_worker.translation_queue,
        target_language
    )

    stt_worker.start()

    translation_worker.start()

    tts_worker.start()

    stream.start()

    print(
        "\nLive Translator Running...\n"
    )

    try:

        while True:

            chunk = stream.get_chunk()

            vad.process_chunk(chunk)

    except KeyboardInterrupt:

        print(
            "\nStopping..."
        )

        stt_worker.stop()

        translation_worker.stop()

        tts_worker.stop()

        stream.stop()


if __name__ == "__main__":
    main()