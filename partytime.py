from StringIO import StringIO
from PIL import Image
from pprint import pprint
import os
import re
import requests
import subprocess
import sys
import time

current = { 'name': ""}
brightness = 40

def getLatest():
  proxy = "http://52.26.44.83/"
  r = requests.get(proxy)
  if (r.status_code != 200):
    print "Could not fetch latest: ", r.status_code
    return
  return r.json()

def getExtension(url):
  # get file extension
  matches = re.search(r'\.\w+$', url, re.M)
  extension = matches.group(0)
  return extension

def getEmoji(name, url, extension):
  filename = "/home/pi/emoji/"+ name + extension
  child = subprocess.Popen([
    'wget',
    '-nv',
    '-O', 
    filename,
    url])
  while child.poll() is None:
    time.sleep(0.1)
  return filename

def showImage():
  try:
    args = [
      '/home/pi/led-image-viewer', 
      '--led-slowdown-gpio=2',
      '--led-gpio-mapping=adafruit-hat-pwm',
      '--led-brightness=' + str(brightness),
      '-L',
      '-f',
      current['filename']
    ]
    FNULL = open(os.devnull, 'w')
    child = subprocess.Popen(args, stdout=FNULL, stderr=subprocess.STDOUT)
    while child.poll() is None:
      if (checkIfChanged()):
        child.kill()
        return
      time.sleep(1)
  except subprocess.CalledProcessError, e:
    print "error:", e.output

def checkIfChanged():
  global current
  latest = getLatest()
  if (latest['name'] != current['name']):
    extension = getExtension(latest['url'])
    filename = getEmoji(latest['name'], latest['url'], extension)
    current = {
      'name': latest['name'],
      'filename': filename,
      'extension': extension
    }
    print "Got new emoji: " + latest['name']
    return 1
  return 0

try:
  while True:
    checkIfChanged()
    showImage()

except KeyboardInterrupt:
  sys.exit(0)




