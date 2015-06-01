#!/usr/bin/env python

# "Arduino companion"
# test implm of a LEDs animations using an Arduino Micro & 74HC595 shift registers 

import serial  # needed for serial communication with the uC/Arduino
import time

# initial setup
# init the Arduino serial connection
#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=None)
try:
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=None)
except (OSError, IOError) as e:
    print "' should connect uC/Arduino first ;p !"
    quit()

while 1 == 1:

  # test pattern: all outputs of the first shift register HIGH
  #ser.write( '0/0/0/0/0/0/0/0/1/1/1/1/1/1/1/1\n' )
  ser.write( '1/1/1/1/1/1/1/1/0/0/0/0/0/0/0/0\n' )

  uCmessage = ser.readline()
  print uCmessage
  
  time.sleep( 2 )

# close the serial connection with the uC/Arduino
ser.close()
