import time
import sounddevice as sd
from scipy.io.wavfile import write


OUTPUT_FILE = "outputs/input.wav"
SAMPLE_RATE = 48000
DURATION = 5
DEVICE_ID = 5


def record_audio(status_callback=None):

    if status_callback:
        status_callback("Starting in 3...")

    time.sleep(1)

    if status_callback:
        status_callback("Starting in 2...")

    time.sleep(1)

    if status_callback:
        status_callback("Starting in 1...")

    time.sleep(1)

    if status_callback:
        status_callback("Recording...")

    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        device=DEVICE_ID
    )

    sd.wait()

    write(
        OUTPUT_FILE,
        SAMPLE_RATE,
        recording
    )

    if status_callback:
        status_callback("Recording Complete")

    return OUTPUT_FILE