from streaming.audio_stream import AudioStream
from streaming.vad_detector import VADDetector
from streaming.worker import (
    STTWorker,
    TranslationWorker
)

from models.model_manager import (
    ModelManager
)


def main():

    manager = ModelManager()

    manager.load_models()

    stream = AudioStream()

    vad = VADDetector(
        silence_duration=1.5
    )

    stt_worker = STTWorker(
        manager.whisper_model,
        vad.speech_queue
    )

    translation_worker = TranslationWorker(
        manager.translator_model,
        manager.tokenizer,
        stt_worker.text_queue,
        "hin_Deva"
    )

    stt_worker.start()

    translation_worker.start()

    stream.start()

    print(
        "\nStreaming Translation Started\n"
    )

    try:

        while True:

            chunk = stream.get_chunk()

            vad.process_chunk(chunk)

            while (
                not translation_worker
                .translation_queue.empty()
            ):

                translated_text = (
                    translation_worker
                    .translation_queue
                    .get()
                )

                print(
                    "\nTranslated:"
                )

                print(
                    translated_text
                )

                print()

    except KeyboardInterrupt:

        stt_worker.stop()

        translation_worker.stop()

        stream.stop()


if __name__ == "__main__":
    main()