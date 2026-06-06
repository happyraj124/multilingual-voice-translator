"""
pipeline/speech_to_translation.py

FIX 8: The original file had no run_pipeline() function — main.py calls
        run_pipeline(manager) but it was never defined here, causing an
        immediate ImportError / NameError at startup.
        Added run_pipeline() with an interactive loop.

FIX 9: WHISPER_TO_NLLB was duplicated here and in language_manager.py.
        Consolidated — now imported from tts.language_manager.

IMPROVEMENT: run_pipeline() prompts the user to pick a target language
             and loops continuously for a true live-translation experience.
"""

import threading

from audio.recorder import record_audio
from stt.whisper_engine import transcribe_audio
from translation.translator import translate_text
from tts.tts_engine import speak
from tts.language_manager import WHISPER_TO_NLLB, NLLB_TO_MMS

LANGUAGE_MENU = {
    "1": ("eng_Latn", "English"),
    "2": ("hin_Deva", "Hindi"),
    "3": ("urd_Arab", "Urdu"),
    "4": ("spa_Latn", "Spanish"),
    "5": ("fra_Latn", "French"),
    "6": ("deu_Latn", "German"),
    "7": ("por_Latn", "Portuguese"),
    "8": ("ara_Arab", "Arabic"),
}


def _pick_language(prompt: str) -> str | None:
    """Show language menu and return NLLB code, or None for auto."""
    print(f"\n{prompt}")
    print("  0. Auto-detect")
    for key, (code, name) in LANGUAGE_MENU.items():
        print(f"  {key}. {name} ({code})")
    choice = input("Enter number: ").strip()
    if choice == "0":
        return None
    return LANGUAGE_MENU.get(choice, (None, None))[0]


def process_audio(
    manager,
    source_lang: str | None,
    target_lang: str,
    status_callback=None
) -> tuple[str, str, str]:
    """
    Full pipeline: record → STT → translate → TTS.

    Returns (source_text, translated_text, detected_language).
    """
    # Step 1: Record
    audio_path = record_audio(status_callback=status_callback)

    # Step 2: STT
    if status_callback:
        status_callback("Transcribing...")

    # FIX 3 propagated: pass language=None for auto-detect unless forced
    whisper_lang = None
    if source_lang is not None:
        # reverse-map NLLB code → Whisper code for forced language
        rev = {v: k for k, v in WHISPER_TO_NLLB.items()}
        whisper_lang = rev.get(source_lang)

    stt_result = transcribe_audio(
        manager.whisper_model,
        audio_path,
        language=whisper_lang
    )

    source_text = stt_result["text"]
    detected_language = stt_result["language"]

    if status_callback:
        status_callback(f"Detected: {detected_language}")

    # Auto-detect source lang if not forced
    if source_lang is None:
        source_lang = WHISPER_TO_NLLB.get(detected_language, "eng_Latn")

    # Step 3: Translation
    if status_callback:
        status_callback("Translating...")

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

    # Step 4: TTS (non-blocking)
    if status_callback:
        status_callback("Speaking...")

    threading.Thread(
        target=speak,
        args=(translated_text, target_lang),
        daemon=True
    ).start()

    return source_text, translated_text, detected_language


def run_pipeline(manager) -> None:  # FIX 8: was missing entirely
    """
    Interactive live-translation loop.
    Prompts for target language then loops: record → transcribe → translate → speak.
    """
    print("\n=== MULTILINGUAL VOICE TRANSLATOR ===")

    target_lang = _pick_language("Select TARGET language (output):") or "hin_Deva"
    source_lang = _pick_language("Select SOURCE language (input, 0=auto-detect):")

    print("\nStarting live translation. Press Ctrl+C to quit.\n")

    while True:
        try:
            source_text, translated_text, detected = process_audio(
                manager=manager,
                source_lang=source_lang,
                target_lang=target_lang,
                status_callback=print
            )

            print(f"\n[Detected language : {detected}]")
            print(f"[Original  ] {source_text}")
            print(f"[Translated] {translated_text}\n")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nTranslation stopped.")
            break
        except Exception as e:
            print(f"\n[Pipeline Error] {e}")
            print("Retrying...\n")
