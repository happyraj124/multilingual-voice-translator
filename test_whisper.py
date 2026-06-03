import whisper

print("Loading model...")

model = whisper.load_model("small")

result = model.transcribe(
    "outputs/input.wav",
    language="hi",
    fp16=False,
    temperature=0
)

print("\nTEXT:")
print(result["text"])

print("\nLANG:")
print(result["language"])