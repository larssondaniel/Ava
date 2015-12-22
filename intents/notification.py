#!/usr/bin/env python

import time
import os
from datetime import datetime
from datetime import date
from threading import Timer

activeReminders = []

def notification(parameters, speech):
  activeReminders.append(Notification(parameters))
  s = speech.encode('utf-8')
  os.system("say '" + s + "'")

class Notification:

  def __init__(self, parameters):
    self.parameters = parameters
    self.text = parameters['text']
    self.timeString = parameters['time']

    currentTime = time.strftime("%H:%M:%S")

    self.reminderTimeInSeconds = sum(int(x) * 60 ** i for i,x in enumerate(reversed(self.timeString.split(":"))))
    self.currentTimeInSeconds = sum(int(x) * 60 ** i for i,x in enumerate(reversed(currentTime.split(":"))))
    self.commit()

  def commit(self):
    Timer(self.reminderTimeInSeconds - self.currentTimeInSeconds, self.remindEvent, ()).start()

  def remindEvent(self):
    os.system("say 'Hey Daniel, " + self.text + "'")