import librosa
import soundfile as sf


def transcribe_audio(
    whisper_model,
    audio_path
):

    # Convert to 16 kHz
    audio, sr = librosa.load(
        audio_path,
        sr=16000
    )

    temp_audio_path = "outputs/temp.wav"

    sf.write(
        temp_audio_path,
        audio,
        16000
    )

    result = whisper_model.transcribe(
        temp_audio_path,
        language="hi",
        fp16=False,
        beam_size=5,
        temperature=0
    )

    return {
        "text": result["text"].strip(),
        "language": result["language"]
    }