from scipy.io import wavfile

sr, data = wavfile.read(
    "outputs/input.wav"
)

print("Sample Rate:", sr)
print("Shape:", data.shape)
print("Dtype:", data.dtype)

print("Min:", data.min())
print("Max:", data.max())