from audio.recorder import record_audio

from stt.whisper_engine import (
    transcribe_audio
)

from translation.translator import (
    translate_text
)

from tts.tts_engine import speak


WHISPER_TO_NLLB = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "ur": "urd_Arab",
    "es": "spa_Latn",
    "fr": "fra_Latn"
}


def process_audio(
    manager,
    source_lang,
    target_lang,
    status_callback=None
):

    # ==========================
    # Step 1: Record Audio
    # ==========================

    audio_path = record_audio(
        status_callback=status_callback
    )

    # ==========================
    # Step 2: Speech-to-Text
    # ==========================

    if status_callback:
        status_callback(
            "Transcribing..."
        )

    stt_result = transcribe_audio(
        manager.whisper_model,
        audio_path
    )

    source_text = stt_result["text"]

    detected_language = stt_result["language"]

    if status_callback:
        status_callback(
            f"Detected: {detected_language}"
        )

    # ==========================
    # Auto Detect Handling
    # ==========================

    if source_lang is None:

        source_lang = (
            WHISPER_TO_NLLB.get(
                detected_language,
                "eng_Latn"
            )
        )

    # ==========================
    # Step 3: Translation
    # ==========================

    if status_callback:
        status_callback(
            "Translating..."
        )

    if source_lang == target_lang:

        translated_text = source_text

    else:

        translated_text = translate_text(
            text=source_text,
            tokenizer=manager.tokenizer,
            translator_model=manager.translator_model,
            source_lang=source_lang,
            target_lang=target_lang
        )

    # ==========================
    # Step 4: Text-to-Speech
    # ==========================

    if status_callback:
        status_callback(
            "Speaking..."
        )

    speak(translated_text)

    # ==========================
    # Return Results
    # ==========================

    return (
        source_text,
        translated_text,
        detected_language
    )