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


def process_audio(manager, status_callback=None):

    # Step 1: Record

    audio_path = record_audio(
        status_callback=status_callback
    )

    if status_callback:
        status_callback("Transcribing...")

    # Step 2: STT

    stt_result = transcribe_audio(
        manager.whisper_model,
        audio_path
    )

    source_text = stt_result["text"]

    language = stt_result["language"]

    if status_callback:
        status_callback(
            f"Detected: {language}"
        )

    # Step 3: Translation

    nllb_src_lang = (
        WHISPER_TO_NLLB.get(
            language,
            "eng_Latn"
        )
    )

    nllb_tgt_lang = "eng_Latn"

    if status_callback:
        status_callback(
            "Translating..."
        )

    translated_text = translate_text(
        text=source_text,
        tokenizer=manager.tokenizer,
        translator_model=manager.translator_model,
        source_lang=nllb_src_lang,
        target_lang=nllb_tgt_lang
    )

    # Step 4: TTS

    if status_callback:
        status_callback(
            "Speaking..."
        )

    speak(translated_text)

    return (
        source_text,
        translated_text,
        language
    )