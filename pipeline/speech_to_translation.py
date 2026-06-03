from audio.recorder import record_audio

from stt.whisper_engine import (
    transcribe_audio
)

from translation.translator import (
    translate_text
)

from tts.tts_engine import speak

# 1. Added "ur" (Urdu) to handle Whisper's confusion between Hindi/Urdu
WHISPER_TO_NLLB = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "ur": "urd_Arab", 
    "es": "spa_Latn",
    "fr": "fra_Latn"
}

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

        # Map Whisper's detected language to NLLB's format
        nllb_src_lang = WHISPER_TO_NLLB.get(language, "eng_Latn")
        
        # 2. FORCE target language to always be English
        nllb_tgt_lang = "eng_Latn" 

        translated_text = translate_text(
            text=source_text,
            tokenizer=manager.tokenizer,
            translator_model=manager.translator_model,
            source_lang=nllb_src_lang,
            target_lang=nllb_tgt_lang
        )

        print("\nTranslation:")
        print(translated_text)

        print("\n===== STEP 4 : SPEAK =====")

        speak(translated_text)