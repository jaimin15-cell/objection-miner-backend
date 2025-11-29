import pyttsx3
import wave
import array

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set properties
engine.setProperty('rate', 150)  # Speed of speech

# Create a simple sales call transcript
text = "Hello, this is a test sales call. The product looks great but the price seems a bit high. We are currently using a competitor product from Acme Corp. Can you tell me more about your features?"

# Save to WAV file
engine.save_to_file(text, 'real_sales_call.wav')
engine.runAndWait()

print("Real audio file 'real_sales_call.wav' created successfully!")
