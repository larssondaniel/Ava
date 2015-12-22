#!/usr/bin/env python

import os

def wisdom(speech, parameters=None):
  s = speech.encode('utf-8')
  os.system("say '" + s + "'")