from audio.recorder import record_audio

from stt.whisper_engine import (
    transcribe_audio
)

from translation.translator import (
    translate_text
)

from tts.tts_engine import speak


def run_pipeline(manager):

    while True:

        choice = input(
            "\nPress ENTER to record (q to quit): "
        )

        if choice.lower() == "q":
            break

        print("\n===== STEP 1 : RECORD =====")

        audio_path = record_audio()

        print("\n===== STEP 2 : STT =====")

        stt_result = transcribe_audio(
            manager.whisper_model,
            audio_path
        )

        source_text = stt_result["text"]
        language = stt_result["language"]

        print("\nDetected Language:")
        print(language)

        print("\nSource Text:")
        print(source_text)

        print("\n===== STEP 3 : TRANSLATE =====")

        translated_text = translate_text(
            source_text,
            manager.tokenizer,
            manager.translator_model
        )

        print("\nTranslation:")
        print(translated_text)

        print("\n===== STEP 4 : SPEAK =====")

        speak(translated_text)