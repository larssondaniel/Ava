#!/usr/bin/env python

import os
from github import Github

g = Github("larssondaniel", "Emapema1337!")
repo = g.get_user().get_repo("Ava")
labelName = "Generated"

def issues(speech, parameters=None):
  t = parameters['text']
  text = t[0].upper() + t[1:]
  if text is not None:
    issue = repo.create_issue(text, labels=[repo.get_label(labelName)])

  s = speech.encode('utf-8')
  os.system("say '" + s + "'")