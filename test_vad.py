from streaming.audio_stream import AudioStream
from streaming.vad_detector import VADDetector


def main():

    stream = AudioStream()

    vad = VADDetector()

    stream.start()

    print("\nSpeak...\n")

    try:

        while True:

            chunk = stream.get_chunk()

            vad.process_chunk(chunk)

            while not vad.speech_queue.empty():

                segment = vad.get_segment()

                print(
                    f"Detected Segment: "
                    f"{len(segment)/16000:.2f}s"
                )

    except KeyboardInterrupt:

        stream.stop()


if __name__ == "__main__":
    main()