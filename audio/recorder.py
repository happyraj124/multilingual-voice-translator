import time
import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(
    output_path="outputs/input.wav",
    duration=5,
    sample_rate=48000
):
    print("\nRecording starts in...")

    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)

    print("Speak now!")

    start = time.time()

    # Device is set to None to let the system automatically select the default mic
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        device=None
    )

    sd.wait()

    end = time.time()

    print(f"Recording duration: {end-start:.2f} seconds")

    write(
        output_path,
        sample_rate,
        audio
    )

    print("Recording saved!")

    return output_path