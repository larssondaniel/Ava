#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path, sys

try:
  import apiai
except ImportError:
  sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
  import apiai

import time
import scipy.io.wavfile as wav

CLIENT_ACCESS_TOKEN = '9b077f65bd9549abbf8dff4b9c58ea77'
SUBSCRIPTION_KEY = 'a15b908f-ce1b-4527-a2ec-86097bc57e12'

def main():
	ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIPTION_KEY)

	request = ai.text_request()

	request.query = "Hello"

	response = request.getresponse()

	print (response.read())

if __name__ == '__main__':
  main()