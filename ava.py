#!/usr/bin/env python
import pkgutil

import os.path, sys, json, time
import intents
from threading import Timer
import pyaudio
# from AppKit import NSSpeechSynthesizer
import os
from collections import deque
import math
import audioop

try:
  import apiai
except ImportError:
  sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
  import apiai

import time
import scipy.io.wavfile as wav

# CHUNK = 512
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# RECORD_SECONDS = 2

RECORD_SECONDS = 2

# Microphone stream config.
CHUNK = 1024  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
THRESHOLD = 2500  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 0.5  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.

CLIENT_ACCESS_TOKEN = '9b077f65bd9549abbf8dff4b9c58ea77'
SUBSCRIPTION_KEY = 'a15b908f-ce1b-4527-a2ec-86097bc57e12'

def main():
    # resampler = apiai.Resampler(source_samplerate=RATE)

    router = Router()

    vad = apiai.VAD()

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIPTION_KEY)

    # request = ai.voice_request()

    # def callback(in_data, frame_count, time_info, status):
    #     frames, data = resampler.resample(in_data, frame_count)
    #     state = vad.processFrame(frames)
    #     request.send(data)

    #     if (state == 1):
    #         return in_data, pyaudio.paContinue
    #     else:
    #         return in_data, pyaudio.paComplete

    # p = pyaudio.PyAudio()

    # stream = p.open(format=FORMAT,
    #                 channels=CHANNELS,
    #                 rate=RATE,
    #                 input=True,
    #                 output=False,
    #                 frames_per_buffer=CHUNK,
    #                 stream_callback=callback)

    # stream.start_stream()

    # print ("Say!")

    # try:
    #     while stream.is_active():
    #         time.sleep(0.1)
    # except Exception:
    #     raise e
    # except KeyboardInterrupt:
    #     pass

    # stream.stop_stream()
    # stream.close()
    # p.terminate()

    # print ("Wait for response...")
    # response = request.getresponse()

    request = ai.text_request()

    while True:
      request.query = raw_input('Say something: ')
      response = request.getresponse()

      # Convert bytes to string type and string type to dict
      string = response.read().decode('utf-8')
      json_obj = json.loads(string)

      answer = json_obj['result']['fulfillment']['speech']

      # intent = json_obj['result']['metadata']['intentName']
      action = json_obj['result']['action']
      parameters = json_obj['result']['parameters']
      speech = json_obj['result']['fulfillment']['speech']
      router.handle_intent(action, parameters, speech)
      # os.system("say '" + answer + "'")


          # listen_for_speech(THRESHOLD)
    # p = pyaudio.PyAudio()

    # stream = p.open(format=FORMAT,
    #                 channels=CHANNELS,
    #                 rate=RATE,
    #                 input=True,
    #                 output=False,
    #                 frames_per_buffer=CHUNK,
    #                 stream_callback=callback)

    # stream.start_stream()

    # print ("Say!")

    # try:
    #     while stream.is_active():
    #         time.sleep(0.1)
    # except Exception:
    #     raise e
    # except KeyboardInterrupt:
    #     pass

    # stream.stop_stream()
    # stream.close()
    # p.terminate()

    # print ("Wait for response...")
    # response = request.getresponse()

    # # Convert bytes to string type and string type to dict
    # string = response.read().decode('utf-8')
    # json_obj = json.loads(string)
    # answer = json_obj['result']['fulfillment']['speech']
    # os.system("say '" + answer + "'")
    # print(response.read())

def listen_for_speech(threshold=THRESHOLD):
    """
    Listens to Microphone, extracts phrases from it and sends it to
    Google's TTS service and returns response. a "phrase" is sound
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process
    (-1 for infinite).
    """
    #Open stream
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print "* Listening mic. "
    audio2send = []
    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK
    slid_win = deque(maxlen=SILENCE_LIMIT * rel)
    #Prepend audio from 0.5 seconds before noise was detected
    prev_audio = deque(maxlen=PREV_AUDIO * rel)
    started = False
    response = []

    while True:
        cur_data = stream.read(CHUNK)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        #print slid_win[-1]
        if(sum([x > THRESHOLD for x in slid_win]) > 0):
            if(not started):
                print "Starting record of phrase"
                started = True
            audio2send.append(cur_data)
        elif (started is True):
            print "Finished"
            # The limit was reached, finish capture and deliver.
            filename = save_speech(list(prev_audio) + audio2send, p)
            # Send file to Google and get response
            r = stt_google_wav(filename)

            # Reset all
            started = False
            slid_win = deque(maxlen=SILENCE_LIMIT * rel)
            prev_audio = deque(maxlen=0.5 * rel)
            audio2send = []
            print "Listening ..."
        else:
            prev_audio.append(cur_data)

    print "* Done recording"
    stream.close()
    p.terminate()

    return response


class Router:
  modules = []
  package = intents
  prefix = package.__name__ + "."
  for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
    modules.append(__import__(modname, fromlist="dummy"))

  def handle_intent(self, action, parameters, speech):
    method = None
    intent = action.split('.', 1)[0]
    for module in Router.modules:
      try:
        method = getattr(module, str(intent))
      except:
        pass
    # Downcase first character of intent name
    # s = str(intent)
    # method_name = s[0].lower() + s[1:]
    # Get the method from intents. Default to a lambda.
    # method = getattr(reminders, str(method_name))
    # Call the method as we return it
    if method is not None:
      method(parameters, speech)
    else:
      print "[ " + intent + " ] I'm not sure what to do..."

if __name__ == '__main__':
  main()