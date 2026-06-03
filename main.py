from models.model_manager import (
    ModelManager
)

from pipeline.speech_to_translation import (
    run_pipeline
)


def main():

    print(
        "\nMULTILINGUAL VOICE TRANSLATOR\n"
    )

    manager = ModelManager()

    manager.load_models()

    run_pipeline(manager)


if __name__ == "__main__":
    main()