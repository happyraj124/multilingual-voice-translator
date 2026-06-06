import whisper

from streaming.audio_stream import AudioStream
from streaming.vad_detector import VADDetector
from streaming.worker import STTWorker


def main():

    print("Loading Whisper...")

    model = whisper.load_model(
        "medium"
    )

    stream = AudioStream()

    vad = VADDetector()

    worker = STTWorker(
        model,
        vad.speech_queue
    )

    worker.start()

    stream.start()

    print(
        "\nSpeak naturally...\n"
    )

    try:

        while True:

            chunk = stream.get_chunk()

            vad.process_chunk(
                chunk
            )

            while (
                not worker.text_queue.empty()
            ):

                text = (
                    worker.text_queue.get()
                )

                print(
                    "\nDetected Text:"
                )

                print(text)

                print()

    except KeyboardInterrupt:

        worker.stop()

        stream.stop()


if __name__ == "__main__":
    main()