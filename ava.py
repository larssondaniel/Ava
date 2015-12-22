#!/usr/bin/env python

import os.path, sys, json, time
from intents import reminders
import routes
from threading import Timer
# import pyaudio
# from AppKit import NSSpeechSynthesizer
import os

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

      print json_obj

      answer = json_obj['result']['fulfillment']['speech']

      intent = json_obj['result']['metadata']['intentName']
      parameters = json_obj['result']['parameters']
      print answer
      router.handle_intent(intent, parameters)
      # os.system("say '" + answer + "'")


class Router:

  def handle_intent(self, intent, parameters):
    """Dispatch method"""
    # Downcase first character of intent name
    s = str(intent)
    method_name = s[0].lower() + s[1:]
    # Get the method from intents. Default to a lambda.
    method = getattr(reminders, str(method_name))
    # Call the method as we return it
    method(parameters)

  # def reminders(self):
  #   print "Reminder!!!"

if __name__ == '__main__':
  main()