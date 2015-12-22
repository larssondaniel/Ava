#!/usr/bin/env python

import os

def wisdom(parameters, speech):
  s = speech.encode('utf-8')
  os.system("say '" + s + "'")