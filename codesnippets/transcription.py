#%%
import sounddevice as sd
import soundfile as sf
import os, whisper
import time 

# List all available devices
print(sd.query_devices())

#sd.default.device

# Set the default device (replace 'your device' with the name or ID of your device)
sd.default.device = 14

#sd.default.device

#%%
# Choose your desired sample rate and duration in seconds
samplerate = 44100  
duration = 10 # in seconds

# Beep
os.system('echo -n -e "\a"')

# Use the sounddevice library to record audio
myrecording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, blocking=True)

# Path to file
filepath = 'my_audio_file.wav'

# Use the soundfile library to save the audio in a .wav file
sf.write(filepath, myrecording, samplerate)

# Load the model
print('load model')
start_time = time.time()
model = whisper.load_model("medium")
end_time = time.time()

execution_time = end_time - start_time
print(f"The code executed in {execution_time} seconds")
# start transcription
print('start transcription')
start_time = time.time()
result = model.transcribe(filepath, language="de", fp16=False, verbose=True)
end_time = time.time()

execution_time = end_time - start_time
print(f"The code executed in {execution_time} seconds")

os.remove(filepath)

# Print the transcribed text
print(result["text"])