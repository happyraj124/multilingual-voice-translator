"""
tts/mms_tts.py

FIX 6: winsound.PlaySound() is Windows-only and causes an immediate
        ImportError / crash on Linux and macOS.
        Replaced with sounddevice.play() which is cross-platform.

FIX 7: cache dir was hardcoded to "cache/" (relative) and never created,
        causing a FileNotFoundError on first run.
        Now uses outputs/tts_cache/ and creates it on startup.

IMPROVEMENT: Added a clear error message when TTS fails instead of
             silently crashing in a daemon thread.
"""

import os
import hashlib
import numpy as np
import sounddevice as sd
import soundfile as sf
import torch

from transformers import AutoTokenizer, VitsModel
from tts.language_manager import get_mms_language

# FIX 7: Use outputs/ subdirectory; create it if needed
CACHE_DIR = os.path.join("outputs", "tts_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

MODEL_CACHE: dict = {}


def load_model(nllb_language: str):
    """Load (or return cached) MMS-TTS tokenizer and model for a language."""
    mms_language = get_mms_language(nllb_language)

    if mms_language in MODEL_CACHE:
        return MODEL_CACHE[mms_language]

    model_name = f"facebook/mms-tts-{mms_language}"
    print(f"\nLoading MMS Model: {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = VitsModel.from_pretrained(model_name)
    model.eval()

    MODEL_CACHE[mms_language] = (tokenizer, model)
    return tokenizer, model


def generate_audio(text: str, language_code: str):
    """Generate waveform numpy array + sample_rate for the given text."""
    tokenizer, model = load_model(language_code)

    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        waveform = model(**inputs).waveform

    audio = waveform.squeeze().cpu().numpy()
    return audio, model.config.sampling_rate


def get_cache_path(text: str, language_code: str) -> str:
    key = language_code + text
    filename = hashlib.md5(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{filename}.wav")


def play_audio(path: str) -> None:
    """Play a .wav file using sounddevice (cross-platform)."""  # FIX 6
    data, samplerate = sf.read(path, dtype="float32")
    sd.play(data, samplerate)
    sd.wait()


def speak(text: str, language_code: str) -> None:
    """Generate (or use cached) TTS audio and play it."""
    if not text.strip():
        return

    print("\n[MMS TTS STARTED]")

    try:
        cache_path = get_cache_path(text, language_code)

        if os.path.exists(cache_path):
            print("[CACHE HIT]")
            play_audio(cache_path)
        else:
            print("[CACHE MISS]")
            audio, sample_rate = generate_audio(text, language_code)
            sf.write(cache_path, audio, sample_rate)
            play_audio(cache_path)

        print("[MMS TTS FINISHED]")

    except Exception as e:
        # FIX 6 side effect: daemon thread failures were silent before
        print(f"[MMS TTS ERROR] {e}")
