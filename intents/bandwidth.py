#!/usr/bin/env python

import os, sys, socket, struct, select
from timeit import default_timer as timer
from subprocess import Popen, PIPE

ICMP_ECHO_REQUEST = 8

def bandwidth(speech, parameters=None):
  s = speech.encode('utf-8')
  os.system("say '" + s + "'")

  verbose_ping("google.com")

def checksum(source_string):
  """
  I'm not too confident that this is right but testing seems
  to suggest that it gives the same answers as in_cksum in ping.c
  """
  sum = 0
  countTo = (len(source_string)/2)*2
  count = 0
  while count<countTo:
    thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
    sum = sum + thisVal
    sum = sum & 0xffffffff # Necessary?
    count = count + 2

  if countTo<len(source_string):
    sum = sum + ord(source_string[len(source_string) - 1])
    sum = sum & 0xffffffff # Necessary?

  sum = (sum >> 16)  +  (sum & 0xffff)
  sum = sum + (sum >> 16)
  answer = ~sum
  answer = answer & 0xffff

  # Swap bytes. Bugger me if I know why.
  answer = answer >> 8 | (answer << 8 & 0xff00)

  return answer


def receive_one_ping(my_socket, ID, timeout):
  """
  receive the ping from the socket.
  """
  timeLeft = timeout
  while True:
    startedSelect = timer()
    whatReady = select.select([my_socket], [], [], timeLeft)
    howLongInSelect = (timer() - startedSelect)
    if whatReady[0] == []: # Timeout
      return

    timeReceived = timer()
    recPacket, addr = my_socket.recvfrom(1024)
    icmpHeader = recPacket[20:28]
    type, code, checksum, packetID, sequence = struct.unpack(
        "bbHHh", icmpHeader
    )
    if packetID == ID:
      bytesInDouble = struct.calcsize("d")
      timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
      return timeReceived - timeSent

    timeLeft = timeLeft - howLongInSelect
    if timeLeft <= 0:
      return

def send_one_ping(my_socket, dest_addr, ID):
  """
  Send one ping to the given dest_addr.
  """
  dest_addr  =  socket.gethostbyname(dest_addr)

  # Header is type (8), code (8), checksum (16), id (16), sequence (16)
  my_checksum = 0

  # Make a dummy heder with a 0 checksum.
  header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
  bytesInDouble = struct.calcsize("d")
  data = (192 - bytesInDouble) * "Q"
  data = struct.pack("d", timer()) + data

  # Calculate the checksum on the data and the dummy header.
  my_checksum = checksum(header + data)

  # Now that we have the right checksum, we put that in. It's just easier
  # to make up a new header than to stuff it into the dummy.
  header = struct.pack(
      "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
  )
  packet = header + data
  my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1

def ping(dest_addr, timeout):
  """
  Returns either the delay (in seconds) or none on timeout.
  """
  icmp = socket.getprotobyname("icmp")
  try:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
  except socket.error, (errno, msg):
    if errno == 1:
      # Operation not permitted
      msg = msg + (
          " - Note that ICMP messages can only be sent from processes"
          " running as root."
      )
      raise socket.error(msg)
    raise # raise the original error

  my_ID = os.getpid() & 0xFFFF

  send_one_ping(my_socket, dest_addr, my_ID)
  delay = receive_one_ping(my_socket, my_ID, timeout)

  my_socket.close()
  return delay
do_one = ping # preserve  old name for compatibility

#
def verbose_ping(dest_addr, timeout = 2):
  """
  Send a ping to dest_addr with the given >timeout< and communicate
  the result.
  """
  try:
    delay  =  do_one(dest_addr, timeout)
  except socket.gaierror, e:
    print "failed. (socket error: '%s')" % e[1]

  if delay  ==  None:
    print "failed. (timeout within %ssec.)" % timeout
  else:
    delay  =  delay * 1000
    if delay < 50:
      msg = "Ping seems fine; it is at %0.0f milliseconds" % delay
    elif delay < 200:
      msg = "The ping isn't great, I measured it at %0.0f milliseconds" % delay
    else:
      msg = """Something seems wrong, I measured your ping to be %0.0f milliseconds.
               Checking your bandwidth would take too long.""" % delay
    os.system("say '" + msg + "'")

  print

def check_bandwidth():
  cmd = ['speedtest-cli', '--simple']

  process = Popen(cmd, stdout=PIPE, bufsize=1)
  while True:
    output = process.stdout.readline()
    if output == '' and process.poll() is not None:
      break
    if output:
      print output.strip()
      os.system("say '" + output.strip() + "'")

  p = Popen(cmd, stdout=PIPE, bufsize=1)
  with p.stdout:
    for line in iter(p.stdout.readline, b''):
      print line,
  p.wait() # wait for the subprocess to exit

  os.system("say '" + out + "'")