# # check_mic.py

# import sounddevice as sd

# print(sd.query_devices())
# print("\nDefault Device:")
# print(sd.default.device)

from tts.tts_engine import speak

speak("Hello, this is a test")