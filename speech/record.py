import sys, os, time
import pyaudio
import wave
from tqdm import tqdm 
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 10
where = "office" # home, office, psr, etc.
typ = "bg" # bg, navsa, etc.
device = "mac" # laptop, pi, mac, etc.

tag = "%s_%s_%s" % (where, typ, device)

WAVE_OUTPUT_FILENAME = "%s_%i_%i.wav" % (tag, RATE, RECORD_SECONDS)

if os.path.isfile(WAVE_OUTPUT_FILENAME):
    print "file already exists, exiting"
    sys.exit()
else:
    print "will save to %s" % WAVE_OUTPUT_FILENAME

audio = pyaudio.PyAudio()

def handle_audio(buf, frame_count, time_info, status):
    frames.append(buf)
    return (buf, pyaudio.paContinue)

# start Recording
crappy = False
if crappy:
    for i in range(audio.get_device_count()):
        if "USB PnP" in audio.get_device_info_by_index(i)["name"]: idx = i
    stream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK,input_device_index=idx, stream_callback = handle_audio)
else:
    stream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK, stream_callback = handle_audio)

print "recording..."
frames = []
stream.start_stream()
for i in tqdm(range(10*RECORD_SECONDS)):
    time.sleep(0.1)
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
