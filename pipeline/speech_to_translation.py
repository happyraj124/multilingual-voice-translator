"""
pipeline/speech_to_translation.py  —  with CPU voice preservation
"""

import threading
from audio.recorder import record_audio
from stt.whisper_engine import transcribe_audio
from translation.translator import translate_text
from tts.mms_tts import speak, speak_preserved
from tts.language_manager import WHISPER_TO_NLLB

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

# Session-level voice profile — built once from first recording, reused
_session_voice_profile = None
_profile_lock = threading.Lock()


def reset_voice_profile():
    """Clear cached profile so next recording re-samples the speaker."""
    global _session_voice_profile
    with _profile_lock:
        _session_voice_profile = None


def _build_profile_bg(audio_path: str):
    global _session_voice_profile
    try:
        from speech_preservation.voice_converter import build_voice_profile
        profile = build_voice_profile(audio_path)
        with _profile_lock:
            if _session_voice_profile is None:
                _session_voice_profile = profile
    except Exception as e:
        print(f"[Voice profile] {e}")


def _pick_language(prompt: str):
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
    source_lang,
    target_lang: str,
    status_callback=None,
    preserve_voice: bool = True,
    vc_strength: float = 0.6,
) -> tuple:
    """
    Full pipeline: record → STT → translate → TTS.
    Returns (source_text, translated_text, detected_language).
    """
    global _session_voice_profile

    # ── Record ────────────────────────────────────────────────────────
    audio_path = record_audio(status_callback=status_callback)

    # ── Build voice profile in background while STT runs ─────────────
    profile_thread = None
    if preserve_voice:
        with _profile_lock:
            need_profile = _session_voice_profile is None
        if need_profile:
            if status_callback:
                status_callback("Analysing voice…")
            profile_thread = threading.Thread(
                target=_build_profile_bg, args=(audio_path,), daemon=True
            )
            profile_thread.start()

    # ── STT ───────────────────────────────────────────────────────────
    if status_callback:
        status_callback("Transcribing…")

    whisper_lang = None
    if source_lang is not None:
        rev = {v: k for k, v in WHISPER_TO_NLLB.items()}
        whisper_lang = rev.get(source_lang)

    stt_result = transcribe_audio(
        manager.whisper_model, audio_path, language=whisper_lang
    )
    source_text       = stt_result["text"]
    detected_language = stt_result["language"]

    if status_callback:
        status_callback(f"Detected: {detected_language}")

    if source_lang is None:
        source_lang = WHISPER_TO_NLLB.get(detected_language, "eng_Latn")

    # ── Wait for profile (usually done by now) ────────────────────────
    if profile_thread is not None:
        profile_thread.join(timeout=5.0)

    # ── Translation ───────────────────────────────────────────────────
    if status_callback:
        status_callback("Translating…")

    translated_text = (
        source_text if source_lang == target_lang
        else translate_text(
            text=source_text,
            tokenizer=manager.tokenizer,
            translator_model=manager.translator_model,
            source_lang=source_lang,
            target_lang=target_lang,
        )
    )

    # ── TTS ───────────────────────────────────────────────────────────
    if preserve_voice:
        if status_callback:
            status_callback("Speaking (voice preserved)…")
        with _profile_lock:
            profile = _session_voice_profile
        threading.Thread(
            target=speak_preserved,
            args=(translated_text, target_lang, profile, vc_strength),
            daemon=True,
        ).start()
    else:
        if status_callback:
            status_callback("Speaking…")
        threading.Thread(
            target=speak, args=(translated_text, target_lang), daemon=True
        ).start()

    return source_text, translated_text, detected_language


def run_pipeline(manager) -> None:
    print("\n=== MULTILINGUAL VOICE TRANSLATOR ===")
    preserve = input("\nEnable voice preservation? (y/n, default y): ").strip().lower()
    preserve_voice = preserve != "n"
    vc_strength = 0.6
    if preserve_voice:
        s = input("Conversion strength 0.1–1.0 (default 0.6): ").strip()
        try:
            vc_strength = max(0.1, min(1.0, float(s)))
        except ValueError:
            pass

    target_lang = _pick_language("Select TARGET language:") or "hin_Deva"
    source_lang = _pick_language("Select SOURCE language (0=auto-detect):")

    print(f"\nVoice preservation: {'ON' if preserve_voice else 'OFF'}")
    print("Press Ctrl+C to quit.\n")

    while True:
        try:
            src, trl, det = process_audio(
                manager, source_lang, target_lang,
                status_callback=print,
                preserve_voice=preserve_voice,
                vc_strength=vc_strength,
            )
            print(f"\n[Detected : {det}]")
            print(f"[Original  ] {src}")
            print(f"[Translated] {trl}\n")
            print("-" * 50)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"\n[Error] {e}\nRetrying…\n")
