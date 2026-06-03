# # test_device_settings.py

# import sounddevice as sd

# print(sd.query_devices(14))

import sounddevice as sd

for i, dev in enumerate(sd.query_devices()):
    if dev["max_input_channels"] > 0:
        print(i, dev["name"])