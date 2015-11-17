#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path, sys, json
import pyaudio
# from AppKit import NSSpeechSynthesizer
import os

try:
  import apiai
except ImportError:
  sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
  import apiai

import time
import scipy.io.wavfile as wav

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 2

CLIENT_ACCESS_TOKEN = '9b077f65bd9549abbf8dff4b9c58ea77'
SUBSCRIPTION_KEY = 'a15b908f-ce1b-4527-a2ec-86097bc57e12'

def main():
    resampler = apiai.Resampler(source_samplerate=RATE)

    vad = apiai.VAD()

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIPTION_KEY)

    request = ai.voice_request()

    def callback(in_data, frame_count, time_info, status):
        frames, data = resampler.resample(in_data, frame_count)
        state = vad.processFrame(frames)
        request.send(data)

        if (state == 1):
            return in_data, pyaudio.paContinue
        else:
            return in_data, pyaudio.paComplete

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=False,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    stream.start_stream()

    print ("Say!")

    try:
        while stream.is_active():
            time.sleep(0.1)
    except Exception:
        raise e
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()

    print ("Wait for response...")
    response = request.getresponse()

    # Convert bytes to string type and string type to dict
    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
    answer = json_obj['result']['fulfillment']['speech']
    os.system("say '" + answer + "'")

if __name__ == '__main__':
  main()