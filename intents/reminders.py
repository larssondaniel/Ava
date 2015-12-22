#!/usr/bin/env python

import time
from datetime import datetime
from datetime import date
from threading import Timer

activeReminders = []

def reminders(parameters):

  activeReminders.append(Reminder(parameters))

class Reminder:

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
    os.system("say '" + self.text + "'")