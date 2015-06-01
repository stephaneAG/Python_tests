# -*- coding: utf-8 -*-

#!/usr/bin/env python


## -*- coding: iso-8859-1 -*-
# the above is to prevent that damn " SyntaxError: Non-ASCII character '\xc2' " error

# "Arduino companion"
# test implm of a LEDs animations using an Arduino Micro & 74HC595 shift registers 

import serial  # needed for serial communication with the uC/Arduino
import time
import sys     # needed to print stuff on the same line in stdout

# initial setup
# init the Arduino serial connection
#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=None)
try:
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=None)
except (OSError, IOError) as e:
    print "' should connect uC/Arduino first ;p !"
    quit()
    



def formatPattern( pattern ):
  return '/'.join( pattern )

    
# define a list of patterns that'll loop through
# aka quick test before writing a simple module that 'll alter a provided pattern
curr_pattern_idx = 0;

# simplest for quick test & debug
#patterns = ['A', 'B', 'C']

#pattern: one shift register at a time
'''
patterns = [
    '0000000011111111', 
    '1111111100000000'
    ]
'''
    
#pattern: K2000 hardcoded animation

#: to reverse a string in Python:
# 'Stephane garnier'[::-1]  # => 'reinrag enahpetS'
#  for item in patterns:
#    print item[::-1]
#    print '/'.join(item[::-1]) # to format it for uC
#    print "'"+item[::-1]+"'," # to copy/paste the result for the below patterns list

patterns = [
    '0000000110000000',
    '0000000011000000',
    '0000000001100000',
    '0000000000110000',
    '0000000000011000',
    '0000000000001100',
    '0000000000000110',
    '0000000000000011', # right most
    '0000000000000001', # right most & cutoff
    '0000000000000011', # right most
    '0000000000000110',
    '0000000000001100',
    '0000000000011000',
    '0000000000110000',
    '0000000001100000',
    '0000000011000000',
    '0000000110000000', # same as starting position, middle
    '0000001100000000',
    '0000011000000000',
    '0000110000000000',
    '0001100000000000',
    '0011000000000000',
    '0110000000000000',
    '1100000000000000', # left most
    '1000000000000000', # left most & cutoff
    '1100000000000000', # left most
    '0110000000000000',
    '0011000000000000',
    '0001100000000000',
    '0000110000000000',
    '0000011000000000',
    '0000001100000000',
    #'0000000110000000', # start position
    ]

    


def nextPattern():
  global curr_pattern_idx
  if curr_pattern_idx < len(patterns)-1:
    curr_pattern_idx += 1
    #print curr_pattern_idx, patterns[curr_pattern_idx]
    return patterns[curr_pattern_idx]
    #return formatPattern( patterns[curr_pattern_idx] )
  else:
    curr_pattern_idx = 0
    #print curr_pattern_idx, patterns[curr_pattern_idx]
    return patterns[curr_pattern_idx]
    #return formatPattern( patterns[curr_pattern_idx] )
  
def prevPattern():
  global curr_pattern_idx
  if curr_pattern_idx > 0:
    curr_pattern_idx -= 1
    #print curr_pattern_idx, patterns[curr_pattern_idx]
    return patterns[curr_pattern_idx]
    #return formatPattern( patterns[curr_pattern_idx] )
  else:
    curr_pattern_idx = len(patterns)-1
    #print curr_pattern_idx, patterns[curr_pattern_idx]
    return patterns[curr_pattern_idx]
    #return formatPattern( patterns[curr_pattern_idx] )
    

while 1 == 1:

  # clear the entire terminal
  sys.stdout.write("\x1b[2J\x1b[H")
  
  newPattern = nextPattern()
  sys.stdout.write( '\n[ PATTERNS TEST ]' )
  sys.stdout.write( '\n\nCurrent pattern: \n' + newPattern )
  sys.stdout.write( '\n\nFormatted: \n' + formatPattern( newPattern ) )
  
  # test pattern: all outputs of the first shift register HIGH
  #ser.write( '0/0/0/0/0/0/0/0/1/1/1/1/1/1/1/1\n' )
  #ser.write( '1/1/1/1/1/1/1/1/0/0/0/0/0/0/0/0\n' )
  ser.write( formatPattern( newPattern )+'\n' )
  uCmessage = ser.readline()
#  print uCmessage
  sys.stdout.write( '\n\nuC/Arduino callback: \n' + uCmessage )
  
  sys.stdout.flush()
  
  
  time.sleep( 0.100 )

# close the serial connection with the uC/Arduino
ser.close()
