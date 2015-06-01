#!/usr/bin/env python

# "Arduino companion"
# test-implm of a python-based keyboard keys events handler to interface an Arduino connected to an Xbox Controller S

#--------------------------------------------
# import the needed libraries
import time    # needed for delaying execution
import serial  # needed for serial communication with the uC/Arduino
import sys     # needed to print stuff on the same line in stdout
import pyxhook # needed to handle keyboard key events ( press & release )


#--------------------------------------------
# define the Arduino event states URI chunks -> those will be updated & used a the event states URI chunks, & also allows us to have the needed defaults in our URI
read_chunk_C1  = '0'   # chunk #1  ( ltrig )
read_chunk_H1  = '0'   # chunk #2  ( rtrig )
read_chunk_C2  = '128' # chunk #3  ( ljoyY )      / resting voltage 2.3V on 4.6V
read_chunk_H2  = '128' # chunk #4  ( rjoyY )      / resting voltage 2.3V on 4.6V
read_chunk_C3  = '128' # chunk #5  ( ljoyX )      / resting voltage 2.3V on 4.6V
read_chunk_H3  = '128' # chunk #6  ( rjoyX )      / resting voltage 2.3V on 4.6V
read_chunk_C4  = '1'   # chunk #7  ( ljoyS )      / HIGH by default ( 4.4V on 4.6V )
read_chunk_H4  = '1'   # chunk #8  ( rjoyS )      / HIGH by default ( 4.4V on 4.6V )
read_chunk_C5  = '1'   # chunk #9  ( btnBack )    / HIGH by default ( 4.4V on 4.6V )
read_chunk_H5  = '0'   # chunk #10 ( btnBlack )
read_chunk_C6  = '1'   # chunk #11 ( btnStart )   / HIGH by default ( 4.4V on 4.6V )
read_chunk_H6  = '0'   # chunk #12 ( btnWhite )
read_chunk_C7  = '1'   # chunk #13 ( keypadUp )   / HIGH by default ( 4.4V on 4.6V )
read_chunk_H7  = '0'   # chunk #14 ( btnY )
read_chunk_C8  = '1'   # chunk #15 ( keypadDown ) / HIGH by default ( 4.4V on 4.6V )
read_chunk_H8  = '0'   # chunk #16 ( btnA )
read_chunk_C9  = '1'   # chunk #17 ( keypadLeft ) / HIGH by default ( 4.4V on 4.6V )
read_chunk_H9  = '0'   # chunk #18 ( btnX )
read_chunk_C10 = '1'   # chunk #19 ( keypadRight ) / HIGH by default ( 4.4V on 4.6V )
read_chunk_H10 = '0'   # chunk #20 ( btnB )


#--------------------------------------------
# define the states of the keyboard keys associated with the Xbox Controller S controls ( triggers, joystick(s), & buttons )
# Nb: not all the controls are defined, but the minimum needed to play emulated games
# Nb2: as we're using Python, we use a dictionary to hold these
controlsStates = { 'ltrig': 'up', 'rtrig': 'up', 'ljoyUp': 'up', 'ljoyDown': 'up', 'ljoyLeft': 'up', 'ljoyRight': 'up', 'ljoySelect': 'up', 'btnY': 'up', 'btnA': 'up', 'btnX': 'up', 'btnB': 'up', 'btnBack': 'up', 'btnStart': 'up', 'keypadUp': 'up', 'keypadDown': 'up' }
# R: to access one of the dict's key's value, we just have to do so:
# controlsStates['btnA']
# R2: to concatenate all our stuff into an "event states URI", we just have to do so:
# eventStatesURI = read_chunk_H9+"/"+read_chunk_H9

# define the keyboard keys we'll be handling to udate the above control states


#--------------------------------------------
# Function to update the control's states based on the key press / key release events we handle using pyxhook
def keyboardKeyPress( event ):
    if event.Ascii == 32: #If the ascii value matches spacebar, terminate the while loop
        global running
        running = False
    else:
        keyboardEvent( event )

def keyboardKeyRelease( event ):
    keyboardEvent( event )

def keyboardEvent( event ):
    print 'messageName: ', event.MessageName
    print 'message: ', event.Message
    print 'time: ', event.Time
    print 'window: ', event.Window
    print 'WindowName: ', event.WindowName
    print 'Ascii: ', event.Ascii
    print 'Key: ', event.key
    print 'KeyID: ', event.KeyID
    print 'ScanCode: ', event.ScanCode
    print 'Extended: ', event.Extended
    print 'Injected: ', event.Injected
    print 'Alt: ', event.Alt
    print 'Transition: ', event.Transition
    print '---'
    
    return True # we return True to pass the vent to other handlers

#--------------------------------------------
# Function to update the controls chunks based on the current control's states
def updateChunks():
    # triggers
    read_chunk_C1 = '1' if controlsStates['ltrig'] == 'down' else '0'
    read_chunk_H1 = '1' if controlsStates['rtrig'] == 'down' else '0'
    # left joystick Y - resting voltage 2.3V on 4.6V
    if controlsStates['ljoyUp'] == 'down' and controlsStates['ljoyDown'] == 'up':
        read_chunk_C2 = '255' # go upward
    elif controlsStates['ljoyDown'] == 'down' and controlsStates['ljoyUp'] == 'up':
        read_chunk_C2 = '0' # go backward
    else :
        read_chunk_C2 = '128' # stay still
        
    # left joystick X - resting voltage 2.3V on 4.6V
    if controlsStates['ljoyLeft'] == 'down' and controlsStates['ljoyRight'] == 'up':
        read_chunk_C3 = '0' # go left
    elif controlsStates['ljoyRight'] == 'down' and controlsStates['ljoyLeft'] == 'up':
        read_chunk_C3 = '255' # go right
    else :
        read_chunk_C3 = '128' # stay still
    
    # left joystick select - HIGH by default ( 4.4V on 4.6V )
    read_chunk_C4 = '0' if controlsStates['ljoySelect'] == 'down' else '1'
    # btns Y,A,X,B
    read_chunk_H7 = '1' if controlsStates['btnY'] == 'down' else '0'
    read_chunk_H8 = '1' if controlsStates['btnA'] == 'down' else '0'
    read_chunk_H9 = '1' if controlsStates['btnX'] == 'down' else '0'
    read_chunk_H10 = '1' if controlsStates['btnB'] == 'down' else '0'
    # btns back & start - HIGH by default ( 4.4V on 4.6V )
    read_chunk_C5 = '0' if controlsStates['btnBack'] == 'down' else '1'
    read_chunk_C6 = '0' if controlsStates['btnStart'] == 'down' else '1'
    # keypad up & down - HIGH by default ( 4.4V on 4.6V )
    read_chunk_C7 = '0' if controlsStates['keypadUp'] == 'down' else '1'
    read_chunk_C8 = '0' if controlsStates['keypadDown'] == 'down' else '1'
    # we already have the defaults for the ones we're not using: H2,H3,H4,H5,H6,C9,C10
    

#--------------------------------------------
# Function to generate the "event states URI" ( wich actually concatenates all the controls states into a string that'll be sent to the uC/Arduino for parsing & further processing )
def generateEventStatesURI():
    #eventStatesURI = read_chunk_H9+"/"+read_chunk_H9
    #eventStatesURI = eventStatesURI+'/'+read_chunk_H9+"/"+read_chunk_H9
    eventStatesURI = read_chunk_C1+'/'+read_chunk_H1+'/'+read_chunk_C2+'/'+read_chunk_H2+'/'+read_chunk_C3+'/'+read_chunk_H3+'/'+read_chunk_C4+'/'+read_chunk_H4
    eventStatesURI = eventStatesURI+'/'+read_chunk_C5+'/'+read_chunk_H5+'/'+read_chunk_C6+'/'+read_chunk_H6+'/'+read_chunk_C7+'/'+read_chunk_H7
    eventStatesURI = eventStatesURI+'/'+read_chunk_C8+'/'+read_chunk_H8+'/'+read_chunk_C9+'/'+read_chunk_H9+'/'+read_chunk_C10+'/'+read_chunk_H10
    return eventStatesURI+'\n'


#--------------------------------------------
# init the Arduino serial connection
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=None)
# init pyxhook to handles key press  & key realease events
hookr = pyxhook.HooManager() # create a hook manager
hookr.keyUp = keyboardKeyPress # define a keyboard key press callback handler
hookr.keyDown = keyboardKeyRelease # define a keyboard key release callback handler
hookr.HookKeyboard() # hook the keyboard .. humm ;p
hookr.start() # start the hookr internal loop .. in that dark alley .. :|


# -- pyxhook loop for key processing --
#--------------------------------------------
# infinite loop
#while 1 == 1 : 
running = True
while running:
  #ser.write('0/0/128/128/128/128/1/1/1/0/1/0/1/0/1/0/1/0/1/0\n') # quick debug test
  
  # -- update --
  updateChunks() # updates the chunks based on keys currently pressed - to be moved as last statement in both keypress & keyrelease events instead of here
  
  # -- serial comm --
  #ser.write( generateEventStatesURI() ) # write the updated event states URI to the uC/Arduino
  #callbackData = ser.readline()
  
  # -- stdout ( terminal ) --
  #print( callbackData )
  #sys.stdout.write( '\r'+ callbackData) # sends only the exact characters to stdout without an implicit newline
  # same as above, in case the uC/Arduino sends back stuff with a linefeed ( '\n' ) & we wanna get rid of it: 
  sys.stdout.write( '\r'+ callbackData.rstrip('\n') )
  sys.stdout.flush() #don't store characters in a buffer rather than printing them immediately
  
  #time.sleep( 0.005 ) # seems to work fine on the Arduino side when just parsing serial& returning corresonding serial without further I/O
  time.sleep( 1 ) # debug


#--------------------------------------------
# cleanup 
ser.close() # close the serial conn with the uC/Arduino
hookr.cancel() # stop hooking ( close the hookr listener when done - aka stop handling keyboard key events )
