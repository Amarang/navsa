import pyaudio
import wave
from tqdm import tqdm 
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 11025
CHUNK = 512
RECORD_SECONDS = 15
WAVE_OUTPUT_FILENAME = "sounds/test.wav"

audio = pyaudio.PyAudio()
 
# start Recording
stream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

print "recording..."
frames = []
 
for i in tqdm(range(0, int(RATE / CHUNK * RECORD_SECONDS))):
    data = stream.read(CHUNK)
    frames.append(data)
print "finished recording"
 
 
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
 
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()
