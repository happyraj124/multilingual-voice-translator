import pyttsx3


def speak(text):

    print("\n[TTS STARTED]")
    print(text)

    engine = pyttsx3.init()

    engine.setProperty("rate", 150)
    engine.setProperty("volume", 1.0)

    engine.say(text)

    engine.runAndWait()

    engine.stop()

    print("[TTS FINISHED]")