import sys, os
import pyaudio
import wave
from tqdm import tqdm 
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 10
where = "home" # home, office, psr, etc.
typ = "navsa" # bg, navsa, etc.
device = "pi" # laptop, pi, mac, etc.

tag = "%s_%s_%s" % (where, typ, device)

WAVE_OUTPUT_FILENAME = "%s_%i_%i.wav" % (tag, RATE, RECORD_SECONDS)

if os.path.isfile(WAVE_OUTPUT_FILENAME):
    print "file already exists, exiting"
    sys.exit()
else:
    print "will save to %s" % WAVE_OUTPUT_FILENAME

audio = pyaudio.PyAudio()


 
# start Recording
crappy = False
if crappy:
    for i in range(audio.get_device_count()):
        if "USB PnP" in audio.get_device_info_by_index(i)["name"]: idx = i
    stream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK,input_device_index=idx)
else:
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
