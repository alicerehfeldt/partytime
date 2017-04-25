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
  try:
    proxy = "http://52.26.44.83/"
    r = requests.get(proxy)
    if (r.status_code != 200):
      print "Could not fetch latest: ", r.status_code
      return False
    return r.json()
  except Exception:
    return False

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
      '-C',
      current['filename']
    ]
    FNULL = open(os.devnull, 'w')
    child = subprocess.Popen(args, stdout=FNULL, stderr=subprocess.STDOUT)
    while child.poll() is None:
      if (checkIfChanged()):
        child.kill()
        return
      time.sleep(3)
  except subprocess.CalledProcessError, e:
    print "error:", e.output

def checkIfChanged():
  global current, brightness
  changed = 0
  latest = getLatest()
  if (latest == False):
    return 0
  if (latest['brightness'] != brightness):
    brightness = latest['brightness']
    print "New brightness: " + str(brightness)
    changed = 1
  if (latest['name'] != current['name']):
    extension = getExtension(latest['url'])
    filename = getEmoji(latest['name'], latest['url'], extension)
    current = {
      'name': latest['name'],
      'filename': filename,
      'extension': extension
    }
    print "Got new emoji: " + latest['name']
    changed = 1
  return changed

while True:
  try:
    checkIfChanged()
    showImage()
  except KeyboardInterrupt:
    sys.exit(0)




