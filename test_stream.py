from streaming.audio_stream import AudioStream


def main():

    stream = AudioStream()

    stream.start()

    try:

        print("Listening...\n")

        while True:

            chunk = stream.get_chunk()

            print(
                f"Received chunk: {chunk.shape}"
            )

    except KeyboardInterrupt:

        stream.stop()


if __name__ == "__main__":
    main()