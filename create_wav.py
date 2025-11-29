import wave
import struct

# Create a dummy .wav file (1 second of silence)
with wave.open("test_audio.wav", "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    f.writeframes(b'\x00\x00' * 44100)

print("Created test_audio.wav")
