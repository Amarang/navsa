#!/usr/bin/env python3

"""Library for performing speech recognition with support for Google Speech Recognition, Wit.ai, IBM Speech to Text, and AT&T Speech to Text."""

__author__ = "Anthony Zhang (Uberi)"
__version__ = "3.1.3"
__license__ = "BSD"

import io, os, subprocess, wave, base64
import math, audioop, collections, threading
import platform, stat, sys, copy
import json
import numpy as np

import Utils as u

try: # try to use python2 module
    from urllib2 import Request, urlopen, URLError, HTTPError
except ImportError: # otherwise, use python3 module
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError

# define exceptions
class WaitTimeoutError(Exception): pass
class RequestError(Exception): pass
class UnknownValueError(Exception): pass

class AudioSource(object):
    def __init__(self): raise NotImplementedError("this is an abstract class")
    def __enter__(self): raise NotImplementedError("this is an abstract class")
    def __exit__(self, exc_type, exc_value, traceback): raise NotImplementedError("this is an abstract class")

import pyaudio
class Microphone(AudioSource):
    """
    This is available if PyAudio is available, and is undefined otherwise.
    Creates a new ``Microphone`` instance, which represents a physical microphone on the computer. Subclass of ``AudioSource``.
    If ``device_index`` is unspecified or ``None``, the default microphone is used as the audio source. Otherwise, ``device_index`` should be the index of the device to use for audio input.
    A device index is an integer between 0 and ``pyaudio.get_device_count() - 1`` (assume we have used ``import pyaudio`` beforehand) inclusive. It represents an audio device such as a microphone or speaker. See the `PyAudio documentation <http://people.csail.mit.edu/hubert/pyaudio/docs/>`__ for more details.
    The microphone audio is recorded in chunks of ``chunk_size`` samples, at a rate of ``sample_rate`` samples per second (Hertz).
    Higher ``sample_rate`` values result in better audio quality, but also more bandwidth (and therefore, slower recognition). Additionally, some machines, such as some Raspberry Pi models, can't keep up if this value is too high.
    Higher ``chunk_size`` values help avoid triggering on rapidly changing ambient noise, but also makes detection less sensitive. This value, generally, should be left at its default.
    """
    def __init__(self, device_index = None, sample_rate = 16000, chunk_size = 512):
        assert device_index is None or isinstance(device_index, int), "Device index must be None or an integer"
        if device_index is not None: # ensure device index is in range
            audio = pyaudio.PyAudio(); count = audio.get_device_count(); audio.terminate() # obtain device count
            assert 0 <= device_index < count, "Device index out of range"
        assert isinstance(sample_rate, int) and sample_rate > 0, "Sample rate must be a positive integer"
        assert isinstance(chunk_size, int) and chunk_size > 0, "Chunk size must be a positive integer"
        self.device_index = device_index
        self.format = pyaudio.paInt16 # 16-bit int sampling
        self.SAMPLE_WIDTH = pyaudio.get_sample_size(self.format) # size of each sample
        self.SAMPLE_RATE = sample_rate # sampling rate in Hertz
        self.CHUNK = chunk_size # number of frames stored in each buffer

        self.audio = None
        self.stream = None

    def __enter__(self):
        assert self.stream is None, "This audio source is already inside a context manager"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            input_device_index = self.device_index, channels = 1,
            format = self.format, rate = self.SAMPLE_RATE, frames_per_buffer = self.CHUNK,
            input = True, # stream is an input stream
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.stream.is_stopped():
            self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.audio.terminate()

class WavFile(AudioSource):
    """
    Creates a new ``WavFile`` instance given a WAV audio file `filename_or_fileobject`. Subclass of ``AudioSource``.

    If ``filename_or_fileobject`` is a string, then it is interpreted as a path to a WAV audio file (mono or stereo) on the filesystem. Otherwise, ``filename_or_fileobject`` should be a file-like object such as ``io.BytesIO`` or similar.

    Note that the WAV file must be in PCM/LPCM format; WAVE_FORMAT_EXTENSIBLE and compressed WAV are not supported and may result in undefined behaviour.
    """

    def __init__(self, filename_or_fileobject):
        if isinstance(filename_or_fileobject, str):
            self.filename = filename_or_fileobject
        else:
            assert filename_or_fileobject.read, "Given WAV file must be a filename string or a file-like object"
            self.filename = None
            self.wav_file = filename_or_fileobject
        self.stream = None
        self.DURATION = None

    def __enter__(self):
        assert self.stream is None, "This audio source is already inside a context manager"
        if self.filename is not None: self.wav_file = open(self.filename, "rb")
        self.wav_reader = wave.open(self.wav_file, "rb")
        assert 1 <= self.wav_reader.getnchannels() <= 2, "Audio must be mono or stereo"
        self.SAMPLE_WIDTH = self.wav_reader.getsampwidth()
        self.SAMPLE_RATE = self.wav_reader.getframerate()
        self.CHUNK = 4096
        self.FRAME_COUNT = self.wav_reader.getnframes()
        self.DURATION = self.FRAME_COUNT / float(self.SAMPLE_RATE)
        self.stream = WavFile.WavStream(self.wav_reader)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename: self.wav_file.close()
        self.stream = None
        self.DURATION = None

    class WavStream(object):
        def __init__(self, wav_reader):
            self.wav_reader = wav_reader

        def read(self, size = -1):
            buffer = self.wav_reader.readframes(self.wav_reader.getnframes() if size == -1 else size)
            if isinstance(buffer, str) and str is not bytes: buffer = b"" # workaround for https://bugs.python.org/issue24608, unfortunately only fixes the issue for little-endian systems
            if self.wav_reader.getnchannels() != 1: # stereo audio
                buffer = audioop.tomono(buffer, self.wav_reader.getsampwidth(), 1, 1) # convert stereo audio data to mono
            return buffer

class AudioData(object):
    def __init__(self, frame_data, sample_rate, sample_width):
        assert sample_rate > 0, "Sample rate must be a positive integer"
        assert sample_width % 1 == 0 and sample_width > 0, "Sample width must be a positive integer"
        self.frame_data = frame_data
        self.sample_rate = sample_rate
        self.sample_width = int(sample_width)

    def get_wav_data(self):
        """
        Returns a byte string representing the contents of a WAV file containing the audio represented by the ``AudioData`` instance.

        Writing these bytes directly to a file results in a valid WAV file.
        """
        with io.BytesIO() as wav_file:
            wav_writer = wave.open(wav_file, "wb")
            try: # note that we can't use context manager due to Python 2 not supporting it
                wav_writer.setframerate(self.sample_rate)
                wav_writer.setsampwidth(self.sample_width)
                wav_writer.setnchannels(1)
                wav_writer.writeframes(self.frame_data)
            finally:  # make sure resources are cleaned up
                wav_writer.close()
            wav_data = wav_file.getvalue()
        return wav_data

class Recognizer(AudioSource):
    def __init__(self):
        """
        Creates a new ``Recognizer`` instance, which represents a collection of speech recognition functionality.
        """
        self.params = {}
        self.params["energy_threshold"] = 600 # minimum audio energy to consider for recording
        self.params["dynamic_energy_threshold"] = True
        self.params["dynamic_energy_adjustment_damping"] = 0.15
        self.params["dynamic_energy_ratio"] = 6.0
        self.params["pause_threshold"] = 0.05 # seconds of non-speaking audio before a phrase is considered complete # NJA change this if we want faster response on keywords
        self.params["phrase_threshold"] = 0.5 # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
        self.params["non_speaking_duration"] = 0.03 # seconds of non-speaking audio to keep on both sides of the recording

        self.params["keyword_how_long_ago"] = 999.9
        self.params["keyword_delay"] = 10.0 # how long (in seconds) to consider things said after keyword as commands, after which we must say keyword again

        self.defaultparams = copy.deepcopy(self.params)

    def changeParam(self, name, val):
        self.params[name] = val

    def getParams(self):
        return self.params

    def record(self, source, duration = None, offset = None):
        """
        Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) starting at ``offset`` (or at the beginning if not specified) into an ``AudioData`` instance, which it returns.

        If ``duration`` is not specified, then it will record until there is no more audio input.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"

        frames = io.BytesIO()
        seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        elapsed_time = 0
        offset_time = 0
        offset_reached = False
        while True: # loop for the total number of chunks needed
            if offset and not offset_reached:
                offset_time += seconds_per_buffer
                if offset_time > offset:
                    offset_reached = True

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0: break

            if offset_reached or not offset:
                elapsed_time += seconds_per_buffer
                if duration and elapsed_time > duration: break

                frames.write(buffer)

        frame_data = frames.getvalue()
        frames.close()
        return AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

    def adjust_for_ambient_noise(self, source, duration = 1):
        """
        Adjusts the energy threshold dynamically using audio from ``source`` (an ``AudioSource`` instance) to account for ambient noise.
        Intended to calibrate the energy threshold with the ambient energy level. Should be used on periods of audio without speech - will stop early if any speech is detected.
        The ``duration`` parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning. This value should be at least 0.5 in order to get a representative sample of the ambient noise.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"
        assert self.params["pause_threshold"] >= self.params["non_speaking_duration"] >= 0

        seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        elapsed_time = 0
        while True:
            elapsed_time += seconds_per_buffer
            if elapsed_time > duration: break
            buffer = source.stream.read(source.CHUNK)
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal
            damping = self.params["dynamic_energy_adjustment_damping"] ** seconds_per_buffer # account for different chunk sizes and rates
            target_energy = energy * self.params["dynamic_energy_ratio"]
            self.params["energy_threshold"] = self.params["energy_threshold"] * damping + target_energy * (1 - damping)

    def listen(self, source, timeout = None):
        """
        Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.
        This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input. The ending silence is not included.
        The ``timeout`` parameter is the maximum number of seconds that it will wait for a phrase to start before giving up and throwing an ``speech_recognition.WaitTimeoutError`` exception. If ``timeout`` is ``None``, it will wait indefinitely.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"
        assert self.params["pause_threshold"] >= self.params["non_speaking_duration"] >= 0

        self.handle_keyword()

        seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        pause_buffer_count = int(math.ceil(self.params["pause_threshold"] / seconds_per_buffer)) # number of buffers of non-speaking audio before the phrase is complete
        phrase_buffer_count = int(math.ceil(self.params["phrase_threshold"] / seconds_per_buffer)) # minimum number of buffers of speaking audio before we consider the speaking audio a phrase
        non_speaking_buffer_count = int(math.ceil(self.params["non_speaking_duration"] / seconds_per_buffer)) # maximum number of buffers of non-speaking audio to retain before and after

        # read audio input for phrases until there is a phrase that is long enough
        elapsed_time = 0 # number of seconds of audio read
        while True:
            frames = collections.deque()

            # store audio input until the phrase starts
            while True:
                elapsed_time += seconds_per_buffer
                self.params["keyword_how_long_ago"] += seconds_per_buffer

                if timeout and elapsed_time > timeout: # handle timeout if specified
                    raise WaitTimeoutError("listening timed out")

                buffer = source.stream.read(source.CHUNK)
                if len(buffer) == 0: break # reached end of the stream
                frames.append(buffer)
                if len(frames) > non_speaking_buffer_count: # ensure we only keep the needed amount of non-speaking buffers
                    frames.popleft()

                # detect whether speaking has started on audio input
                energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal
                print energy, self.params["energy_threshold"], self.params["keyword_how_long_ago"]
                if energy > self.params["energy_threshold"]:
                    break

                # dynamically adjust the energy threshold using assymmetric weighted average
                if self.params["dynamic_energy_threshold"]:
                    damping = self.params["dynamic_energy_adjustment_damping"] ** seconds_per_buffer # account for different chunk sizes and rates
                    target_energy = energy * self.params["dynamic_energy_ratio"]
                    self.params["energy_threshold"] = self.params["energy_threshold"] * damping + target_energy * (1 - damping)

            # read audio input until the phrase ends
            pause_count, phrase_count = 0, 0
            while True:
                elapsed_time += seconds_per_buffer
                self.params["keyword_how_long_ago"] += seconds_per_buffer

                buffer = source.stream.read(source.CHUNK)
                if len(buffer) == 0: break # reached end of the stream
                frames.append(buffer)
                phrase_count += 1

                # check if speaking has stopped for longer than the pause threshold on the audio input
                energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal
                if energy > self.params["energy_threshold"]:
                    pause_count = 0
                else:
                    pause_count += 1

                print phrase_count, pause_count, pause_buffer_count
                if pause_count > pause_buffer_count: # end of the phrase
                    break

            # check how long the detected phrase is, and retry listening if the phrase is too short
            phrase_count -= pause_count
            if phrase_count >= phrase_buffer_count: break # phrase is long enough, stop listening

        # obtain frame data
        for i in range(pause_count - non_speaking_buffer_count): frames.pop() # remove extra non-speaking frames at the end
        frame_data = b"".join(list(frames))

        return AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

    def said_keyword(self):
        # call this when keyword is said
        self.params["keyword_how_long_ago"] = 0.0

    def said_keyword_recently(self):
        # used to see if keyword was said recently
        return self.params["keyword_how_long_ago"] < self.params["keyword_delay"]

    def handle_keyword(self):
        # this will get called in the class automatically to handle changing of parameters after a keywor has been said
        if self.said_keyword_recently():
            # we are in the regime where we can say a command, so change some params to allow for sustained speech NJA
            self.params["pause_threshold"] = 0.8 # seconds of non-speaking audio before a phrase is considered complete # NJA change this if we want faster response on keywords
            self.params["phrase_threshold"] = 0.6 # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
            self.params["non_speaking_duration"] = 0.3 # seconds of non-speaking audio to keep on both sides of the recording
        else:
            # regime where we should listen for keyword
            self.params["pause_threshold"] = self.defaultparams["pause_threshold"]
            self.params["phrase_threshold"] = self.defaultparams["phrase_threshold"]
            self.params["non_speaking_duration"] = self.defaultparams["non_speaking_duration"]


    def listen_in_background(self, source, callback):
        """
        Spawns a thread to repeatedly record phrases from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance and call ``callback`` with that ``AudioData`` instance as soon as each phrase are detected.
        Returns a function object that, when called, requests that the background listener thread stop, and waits until it does before returning. The background thread is a daemon and will not stop the program from exiting if there are no other non-daemon threads.
        Phrase recognition uses the exact same mechanism as ``recognizer_instance.listen(source)``.
        The ``callback`` parameter is a function that should accept two parameters - the ``recognizer_instance``, and an ``AudioData`` instance representing the captured audio. Note that ``callback`` function will be called from a non-main thread.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"
        running = [True]
        def threaded_listen():
            with source as s:
                while running[0]:
                    try: # listen for 1 second, then check again if the stop function has been called
                        audio = self.listen(s, 0.75)

                    except WaitTimeoutError: # listening timed out, just try again
                        pass
                    else:
                        if running[0]: callback(self, audio)
        def stopper():
            running[0] = False
            listener_thread.join() # block until the background thread is done
        listener_thread = threading.Thread(target=threaded_listen)
        listener_thread.daemon = True
        listener_thread.start()
        return stopper


    def recognize_wit(self, audio_data, key, show_all = False):
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Wit.ai API.
        The Wit.ai API key is specified by ``key``. Unfortunately, these are not available without `signing up for an account <https://wit.ai/getting-started>`__ and creating an app. You will need to add at least one intent (recognizable sentence) before the API key can be accessed, though the actual intent values don't matter.
        To get the API key for a Wit.ai app, go to the app settings, go to the section titled "API Details", and look for "Server Access Token" or "Client Access Token". If the desired field is blank, click on the "Reset token" button on the right of the field. Wit.ai API keys are 32-character uppercase alphanumeric strings.
        Though Wit.ai is designed to be used with a fixed set of phrases, it still provides services for general-purpose speech recognition.
        The recognition language is configured in the Wit.ai app settings.
        Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://wit.ai/docs/http/20141022#get-intent-via-text-link>`__ as a JSON dictionary.
        Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the key isn't valid, the quota for the key is maxed out, or there is no internet connection.
        """
        assert isinstance(audio_data, AudioData), "Data must be audio data"
        assert isinstance(key, str), "`key` must be a string"

        wav_data = audio_data.get_wav_data()
        url = "https://api.wit.ai/speech?v=20141022"
        request = Request(url, data = wav_data, headers = {"Authorization": "Bearer {0}".format(key), "Content-Type": "audio/wav"})
        try:
            response = urlopen(request)
        except HTTPError as e:
            raise RequestError("recognition request failed: {0}".format(getattr(e, "reason", "status {0}".format(e.code)))) # use getattr to be compatible with Python 2.6
        except URLError as e:
            raise RequestError("recognition connection failed: {0}".format(getattr(e, "reason", "status {0}".format(e.code)))) # use getattr to be compatible with Python 2.6
        response_text = response.read().decode("utf-8")
        result = json.loads(response_text)

        if show_all: return result

        if "_text" not in result or result["_text"] is None: raise UnknownValueError()
        return result["_text"]

if __name__=='__main__':


    lastnum = 0
    try:
        lastnum = sorted([int(v.split("_")[-1].split(".")[0]) for v in os.listdir("train") if "_" in v])[-1]
    except: pass

    from Process import Processor
    proc = Processor()
    # fname = proc.processTrainingSet(basedir="train/", signalword="oknavsa", savedir="data/")
    proc.loadTrainData("data/imagedata_30_30.npy")

    proc.trainAndTest()

    ifile = lastnum+1
    print 'ifile', ifile

    def callback(recognizer, audio):
        global ifile

        if not recognizer.said_keyword_recently():

            frames = ''.join(audio.frame_data)
            framerate = audio.sample_rate
            data = np.fromstring(frames, 'Int16');
            print "here", len(audio.frame_data), audio.sample_rate, 1.0*len(audio.frame_data)/audio.sample_rate


            # waveFile = wave.open("train/output_%i.wav" % ifile, 'wb')
            # waveFile.setnchannels(1)
            # waveFile.setsampwidth(audio.sample_width)
            # waveFile.setframerate(framerate)
            # waveFile.writeframes(frames)
            # waveFile.close()
            # ifile += 1

            confidence = proc.getKeywordProbability(data, framerate)
            print "---------->",confidence, recognizer.said_keyword_recently()
            if confidence > 0.35:
                u.play("../sounds/notification.wav")
                recognizer.said_keyword()

        else:

            WIT_AI_KEY = "5WGVQPPDHU7JH2J5WDBJHMJLRXB5WDTP" # Wit.ai keys are 32-character uppercase alphanumeric strings
            try:
                print recognizer.recognize_wit(audio, key=WIT_AI_KEY,show_all=True)
            except UnknownValueError:
                print("Wit.ai could not understand audio")
            except RequestError as e:
                print("Could not request results from Wit.ai service; {0}".format(e))

    r = Recognizer()
    m = Microphone()


    stop_listening = r.listen_in_background(m, callback) # `stop_listening` is now a function that, when called, stops background listening

    import time
    try:
        for i in range(15):
            time.sleep(1)
    except KeyboardInterrupt:
        print 'interrupted!'
        stop_listening()

    stop_listening()


