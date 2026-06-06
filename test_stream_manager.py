from models.model_manager import (
    ModelManager
)

from streaming.stream_manager import (
    StreamManager
)


def main():

    manager = ModelManager()

    manager.load_models()

    stream_manager = StreamManager(
        manager,
        target_language="hin_Deva"
    )

    stream_manager.start_streaming()

    try:

        while True:

            stream_manager.process()

    except KeyboardInterrupt:

        stream_manager.stop_streaming()


if __name__ == "__main__":
    main()