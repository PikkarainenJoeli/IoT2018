#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import subprocess
from subprocess import Popen, PIPE
import gi
gi.require_version('Wnck','3.0')
from gi.repository import Wnck

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13,GPIO.IN)
GPIO.setup(11,GPIO.OUT)
GPIO.output(11,0)

screen = Wnck.Screen.get_default()

#init empty window
empty = subprocess.Popen(["firefox","192.168.9.137/black.php","new-window"],start_new_session=True)
#empty = subprocess.Popen(["firefox","www.google.com","new-window"],start_new_session=True)
time.sleep(5)
empty_pid = (empty.pid)
empty_window = None

#init index window
index = subprocess.Popen(["firefox","192.168.9.137","new-window"],start_new_session=True)
#index = subprocess.Popen(["firefox","www.wikipedia.com","new-window"],start_new_session=True)
time.sleep(5)
index_pid = (index.pid)

screen.force_update()
windows = screen.get_windows()
for w in windows:
 w.activate(int(time.time()))
 print(screen.get_active_window())
 print ("Name of window ", w.get_name())
 print ("Class group: ",w.get_class_group())
 print ("Pid: ", w.get_pid())
 print ("\n")

 if w.get_pid() == empty_pid and empty_window is  None:
  empty_window = w
  print("found empty window")

 elif empty_window is not None:
  index_window = w
  print("found index window")
 time.sleep(2)

i = GPIO.input(13)
old_value = i
print ("start detection")

while True:
 print ("i value: ",i)
 time.sleep(0.1)
 i = GPIO.input(13)

 if old_value != i:

  if i == 0:
   print ("No detection",i)
   empty_window.activate(int(time.time()))
   GPIO.output(11,0)
   time.sleep(0.1)
   old_value = 0

  elif i == 1:
   index_window.activate(int(time.time()))
   print ("Something detected",i)
   GPIO.output(11,1)
   time.sleep(0.1)
   old_value = 1

Wnck.ShutDown()

