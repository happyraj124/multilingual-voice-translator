import os
import hashlib
import winsound

import soundfile as sf
import torch

from transformers import (
    AutoTokenizer,
    VitsModel
)

from tts.language_manager import (
    get_mms_language
)

MODEL_CACHE = {}


def load_model(nllb_language):

    mms_language = get_mms_language(
        nllb_language
    )

    if mms_language in MODEL_CACHE:

        return MODEL_CACHE[mms_language]

    model_name = (
        f"facebook/mms-tts-{mms_language}"
    )

    print(
        f"\nLoading MMS Model: {model_name}"
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_name
    )

    model = VitsModel.from_pretrained(
        model_name
    )

    MODEL_CACHE[mms_language] = (
        tokenizer,
        model
    )

    return tokenizer, model


def generate_audio(
    text,
    language_code
):

    tokenizer, model = load_model(
        language_code
    )

    inputs = tokenizer(
        text,
        return_tensors="pt"
    )

    with torch.no_grad():

        waveform = model(
            **inputs
        ).waveform

    return (
        waveform,
        model.config.sampling_rate
    )


def get_cache_path(
    text,
    language_code
):

    key = (
        language_code + text
    )

    filename = hashlib.md5(
        key.encode()
    ).hexdigest()

    return os.path.join(
        "cache",
        f"{filename}.wav"
    )


def play_audio(path):

    winsound.PlaySound(
        path,
        winsound.SND_FILENAME
    )


def speak(
    text,
    language_code
):

    print("\n[MMS TTS STARTED]")

    cache_path = get_cache_path(
        text,
        language_code
    )

    if os.path.exists(cache_path):

        print("[CACHE HIT]")

        play_audio(cache_path)

        print("[MMS TTS FINISHED]")

        return

    print("[CACHE MISS]")

    waveform, sample_rate = generate_audio(
        text,
        language_code
    )

    audio = waveform.squeeze().cpu().numpy()

    sf.write(
        cache_path,
        audio,
        sample_rate
    )

    play_audio(cache_path)

    print("[MMS TTS FINISHED]")