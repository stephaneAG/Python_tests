#!/usr/bin/env python

# "Arduino companion"
# test-implm of a python-based keyboard keys events handler to interface an Arduino connected to an Xbox Controller S

#--------------------------------------------
# import the needed libraries
import os
import sys     # needed to print stuff on the same line in stdout
import subprocess
from termios import tcflush, TCIOFLUSH
import time    # needed for delaying execution
import serial  # needed for serial communication with the uC/Arduino
import pyxhook # needed to handle keyboard key events ( press & release )


# quick fix/hack
xtraSpaces = '                     '

#--------------------------------------------
# define the Arduino event states URI chunks -> those will be updated & used a the event states URI chunks, & also allows us to have the needed defaults in our URI
readChunks = { 
    'C1': '0',   # chunk #1  ( ltrig )
    'H1': '0',   # chunk #2  ( rtrig )
    'C2': '128', # chunk #3  ( ljoyY )      / resting voltage 2.3V on 4.6V
    'H2': '128', # chunk #4  ( rjoyY )      / resting voltage 2.3V on 4.6V
    'C3': '128', # chunk #5  ( ljoyX )      / resting voltage 2.3V on 4.6V
    'H3': '128', # chunk #6  ( rjoyX )      / resting voltage 2.3V on 4.6V
    'C4': '1',   # chunk #7  ( ljoyS )      / HIGH by default ( 4.4V on 4.6V )
    'H4': '1',   # chunk #8  ( rjoyS )      / HIGH by default ( 4.4V on 4.6V )
    'C5': '1',   # chunk #9  ( btnBack )    / HIGH by default ( 4.4V on 4.6V )
    'H5': '0',   # chunk #10 ( btnBlack )
    'C6': '1',   # chunk #11 ( btnStart )   / HIGH by default ( 4.4V on 4.6V )
    'H6': '0',   # chunk #12 ( btnWhite )
    'C7': '1',   # chunk #13 ( keypadUp )   / HIGH by default ( 4.4V on 4.6V )
    'H7': '0',   # chunk #14 ( btnY )
    'C8': '1',   # chunk #15 ( keypadDown ) / HIGH by default ( 4.4V on 4.6V )
    'H8': '0',   # chunk #16 ( btnA )
    'C9': '1',   # chunk #17 ( keypadLeft ) / HIGH by default ( 4.4V on 4.6V )
    'H9': '0',   # chunk #18 ( btnX )
    'C10': '1',  # chunk #19 ( keypadRight ) / HIGH by default ( 4.4V on 4.6V ) 
    'H10': '0' } # chunk #20 ( btnB )

buttonsCodes = {
    'x_key': 53,
    'n_key': 57,
    'f_key': 41,
    'v_key': 55,
    'd_key': 40,
    'g_key': 42,
    'r_key': 27,
    'upArrow_key': 111,
    'downArrow_key': 116,
    'leftArrow_key': 113,
    'rightArrow_key': 114,
    'u_key': 30,
    'i_key': 31,
    'o_key': 32,
    'p_key': 33,
    'enter_key': 36,
    'escape_key': 9,
    'lcontrol_key': 37,
    'rcontrol_key': 105,
    'lalt_key': 64,
    'ralt_key': 108,
    'backspace_key': 22,
    'space_key': 65,
    'superl_key': 133   
}

# R: the key number corresponding to the keys used, this keyboard, & the current keyboard mapping -> the list follows ..
# x     => 53  ( LTRIG )       -> ltrig      => C1
# n     => 57  ( RTRIG )       -> rtrig      => H1
# f     => 41  ( LJOY UP )     -> ljoyY      => C2
# v     => 55  ( LJOY DOWN )   -> ljoyY      => C2
# d     => 40  ( LJOY LEFT )   -> ljoyX      => C3
# g     => 42  ( LJOY RIGHT )  -> ljoyX      => C3
# r     => 27  ( LJOY SELECT ) -> ljoySelect => C4
# UP    => 111 ( BTN Y )       -> btnY       => H7
# DOWN  => 116 ( BTN A )       -> btnA       => H8
# LEFT  => 113 ( BTN X )       -> btnX       => H9
# RIGHT => 114 ( BTN B )       -> btnB       => H10
# u     => 30  ( BTN BACK )    -> btnBack    => C5
# i     => 31  ( BTN START )   -> btnStart   => C6
# o     => 32  ( KEYPAD UP )   -> keypadUp   => C7
# p     => 33  ( KEYPAD DOWN ) -> keypadDown => C8
buttonsMapping = [ 
        ( 'x_key', 'ltrig' ),
        ( 'n_key', 'rtrig' ),
        ( 'f_key', 'ljoyUp' ),
        ( 'v_key', 'ljoyDown' ),
        ( 'd_key', 'ljoyLeft' ),
        ( 'g_key', 'ljoyRight' ),
        ( 'r_key', 'ljoySelect' ),
        ( 'upArrow_key', 'btnY' ),
        ( 'downArrow_key', 'btnA' ),
        ( 'leftArrow_key', 'btnX' ),
        ( 'rightArrow_key', 'btnB' ),
        ( 'u_key', 'btnBack' ),
        ( 'i_key', 'btnStart' ),
        ( 'o_key', 'keypadUp' ),
        ( 'p_key', 'keypadDown' ),
    ]

# new approach
'''
PythonGampepad = [
    { 'chunk': 'C1', 'name': 'ltrig', 'default': '0', 'keyCode': 'X', 'value': '0', 'state': 'up' },
    { 'chunk': 'H1', 'name': 'rtrig', 'default': '0', 'keyCode': 'X', 'value': '0', 'state': 'up' },
]
'''

#--------------------------------------------
# define the states of the keyboard keys associated with the Xbox Controller S controls ( triggers, joystick(s), & buttons )
# Nb: not all the controls are defined, but the minimum needed to play emulated games
# Nb2: as we're using Python, we use a dictionary to hold these
controlsStates = { 'ltrig': 'up', 'rtrig': 'up', 'ljoyUp': 'up', 'ljoyDown': 'up', 'ljoyLeft': 'up', 'ljoyRight': 'up', 'ljoySelect': 'up',
                   'btnY': 'up', 'btnA': 'up', 'btnX': 'up', 'btnB': 'up', 'btnBack': 'up', 'btnStart': 'up',
                   'keypadUp': 'up', 'keypadDown': 'up' }
# R: to access one of the dict's key's value, we just have to do so:
# controlsStates['btnA']
# R2: to concatenate all our stuff into an "event states URI", we just have to do so:
# eventStatesURI = read_chunk_H9+"/"+read_chunk_H9

#define the keyboard keys we'll be handling to udate the above control states
def reflectButtonsMapping( keyCode, controlState ):
    for key, value in buttonsCodes.items():
        #print 'Key: ', item, ' has keyCode:', value # Key: <x_key> has keyCode: <53>
        if int(value) == int(keyCode):
            #print 'Matching keyCode !'
            for item in buttonsMapping:
                if item[0] == key:
                    updateControlState( item[1], controlState )

#--------------------------------------------
# Function to update the control's states based on the key press / key release events we handle using pyxhook
def keyboardKeyPress( event ):
    if event.Ascii == 32 or event.ScanCode == 37: #If value matches spacebar or Ctrl_L, terminate the while loop
        global running
        running = False
        #print 'space !\n'
    else:
        #keyboardEvent( event )
        handleKeyPress( event.ScanCode )
        return False
        

def keyboardKeyRelease( event ):
    #keyboardEvent( event )
    handleKeyRelease( event.ScanCode )
    #print 'key released !\n'
    return False


def keyboardEvent( event ):
    print 'messageName: ', event.MessageName, '\n'
    #print 'message: ', event.Message
    #print 'time: ', event.Time
    print 'window: ', event.Window
    print 'WindowName: ', event.WindowName
    print 'Ascii: ', event.Ascii
    print 'Key: ', event.Key
    print 'KeyID: ', event.KeyID
    print 'ScanCode: ', event.ScanCode
    #print 'Extended: ', event.Extended
    #print 'Injected: ', event.Injected
    #print 'Alt: ', event.Alt
    #print 'Transition: ', event.Transition
    print '---'
    
    #return True # we return True to pass the vent to other handlers
    
# update the controls states based on the key pressed / released


def handleKeyPress( keyCode ):
    tcflush( sys.stdin, TCIOFLUSH )
    '''
    if keyCode == buttonsCodes['x_key']: # ascii 53
        updateControlState( 'ltrig', 'down' )
    elif keyCode == buttonsCodes['n_key']: # ascii 57
        updateControlState( 'rtrig', 'down' )
    elif keyCode == buttonsCodes['f_key']: # ascii 41
        updateControlState( 'ljoyUp', 'down' )
    '''
    #else:
        #print 'unsupported key pressed !'
    
    reflectButtonsMapping( keyCode, 'down' )
        
    #return True # we return True to pass the event to other handlers
    

def handleKeyRelease( keyCode ):
    '''
    if keyCode == buttonsCodes['x_key']: # ascii 53
        updateControlState( 'ltrig', 'up' )
    elif keyCode == buttonsCodes['n_key']: # ascii 57
        updateControlState( 'rtrig', 'up' )
    elif keyCode == buttonsCodes['f_key']: # ascii 41
        updateControlState( 'ljoyUp', 'up' )
    '''
    #else:
        #print 'unsupported key released !'
    
    reflectButtonsMapping( keyCode, 'up' )
     
    #return True # we return True to pass the vent to other handlers
        

#--------------------------------------------
def updateControlState( key, state ):
    controlsStates[key] = state
    #print controlsStates[key]
    
def getControlState( key ):
    return controlsStates[key]


#--------------------------------------------
# Function to update the controls chunks based on the current control's states
def updateChunks():
    #global controlsStates

    # triggers
    readChunks['C1'] = '1' if controlsStates['ltrig'] == 'down' else '0'
    readChunks['H1'] = '1' if controlsStates['rtrig'] == 'down' else '0'
    # left joystick Y - resting voltage 2.3V on 4.6V
    if controlsStates['ljoyUp'] == 'down' and controlsStates['ljoyDown'] == 'up':
        readChunks['C2'] = '255' # go upward
    elif controlsStates['ljoyDown'] == 'down' and controlsStates['ljoyUp'] == 'up':
        readChunks['C2'] = '0' # go backward
    else :
        readChunks['C2'] = '128' # stay still
        
    # left joystick X - resting voltage 2.3V on 4.6V
    if controlsStates['ljoyLeft'] == 'down' and controlsStates['ljoyRight'] == 'up':
        readChunks['C3'] = '0' # go left
    elif controlsStates['ljoyRight'] == 'down' and controlsStates['ljoyLeft'] == 'up':
        readChunks['C3'] = '255' # go right
    else :
        readChunks['C3'] = '128' # stay still
    
    # left joystick select - HIGH by default ( 4.4V on 4.6V )
    readChunks['C4'] = '0' if controlsStates['ljoySelect'] == 'down' else '1'
    # btns Y,A,X,B
    readChunks['H7'] = '1' if controlsStates['btnY'] == 'down' else '0'
    readChunks['H8'] = '1' if controlsStates['btnA'] == 'down' else '0'
    readChunks['H9'] = '1' if controlsStates['btnX'] == 'down' else '0'
    readChunks['H10'] = '1' if controlsStates['btnB'] == 'down' else '0'
    # btns back & start - HIGH by default ( 4.4V on 4.6V )
    readChunks['C5'] = '0' if controlsStates['btnBack'] == 'down' else '1'
    readChunks['C6'] = '0' if controlsStates['btnStart'] == 'down' else '1'
    # keypad up & down - HIGH by default ( 4.4V on 4.6V )
    readChunks['C7'] = '0' if controlsStates['keypadUp'] == 'down' else '1'
    readChunks['C8'] = '0' if controlsStates['keypadDown'] == 'down' else '1'
    
    # we already setup default values for the ones we re not using: H2,H3,H4,H5,H6,C9,C10

#--------------------------------------------
def layoutFormat( chunk ):
    if len( chunk ) < 3:
        str = ''
        for letter in range (3 - len( chunk) ):
            str += ' '
        return str+chunk

#asciiEventStatesChunks = []        
def generateAsciiURI():
    asciiEventStatesChunks = generateEventStatesURI().rstrip('\n').split('/')
    asciiEventStatesChunks[2] = layoutFormat( asciiEventStatesChunks[2] )
    asciiEventStatesChunks[3] = layoutFormat( asciiEventStatesChunks[3] )
    asciiEventStatesChunks[4] = layoutFormat( asciiEventStatesChunks[4] )
    asciiEventStatesChunks[5] = layoutFormat( asciiEventStatesChunks[5] )
    #return asciiEventStatesChunks
    
    

def visualController(): 
    return 'Ascii-Art Controller   '

asciiColorsStatesChunks = [
    '',         # 0/21 ( ltrig ) - \033[7m
    '',         # 1/22 ( rtrig ) - \033[7m
    '',         # 2/23 ( ljoyY ) - \033[7m
    '',  # 3/24 ( rjoyY ) - not used
    '',         # 4/25 ( ljoyX ) - \033[7m
    '',  # 5/26 ( rjoyX ) - not used
    '',         # 6/27 ( ljoySelect ) - \033[7m
    '',  # 7/28 ( rjoySelect ) - not used
    '',         # 8/29 ( ljoy ) - \033[7m - overall
    '',  # 9/30 ( rjoy )- not used - overall
    '',         # 10/31 ( keypadUp ) - \033[7m
    '',         # 11/32 ( btnY ) - \033[7m
    '',         # 12/33 ( keypadDown ) - \033[7m
    '',         # 13/34 ( btnA ) - \033[7m
    '',  # 14/35 ( keypadLeft ) - not used
    '',         # 15/36 ( btnX ) - \033[7m
    '',  # 16/37 ( keypadRight ) - not used
    '',         # 17/38 ( btnB ) - \033[7m
    '',         # 18/39 ( btnBack ) - \033[7m
    '', # 19/40 ( btnWhite ) - not used
    '',         # 20/41 ( btnStart ) - \033[7m
    ''   # 21/42 ( btnBlack ) - not used
]

def updateAsciiColorsStatesChunks():
    # triggers
    asciiColorsStatesChunks[0] = '\033[7m' if controlsStates['ltrig'] == 'down' else ''
    asciiColorsStatesChunks[1] = '\033[7m' if controlsStates['rtrig'] == 'down' else ''
    # left joystick Y - resting voltage 2.3V on 4.6V
    if controlsStates['ljoyUp'] == 'down' and controlsStates['ljoyDown'] == 'up':
        asciiColorsStatesChunks[2] = '\033[7m'
    elif controlsStates['ljoyDown'] == 'down' and controlsStates['ljoyUp'] == 'up':
        asciiColorsStatesChunks[2] = '\033[7m'
    else :
        asciiColorsStatesChunks[2] = '' # stay still
            
    # left joystick X - resting voltage 2.3V on 4.6V
    if controlsStates['ljoyLeft'] == 'down' and controlsStates['ljoyRight'] == 'up':
        asciiColorsStatesChunks[4] = '\033[7m'
    elif controlsStates['ljoyRight'] == 'down' and controlsStates['ljoyLeft'] == 'up':
        asciiColorsStatesChunks[4] = '\033[7m'
    else :
        asciiColorsStatesChunks[4] = '' # stay still
        
    # left joystick select - HIGH by default ( 4.4V on 4.6V )
    asciiColorsStatesChunks[6] = '\033[7m' if controlsStates['ljoySelect'] == 'down' else ''
    
    if controlsStates['ljoyUp'] == 'down' or \
       controlsStates['ljoyDown'] == 'down' or \
       controlsStates['ljoyLeft'] == 'down' or \
       controlsStates['ljoyRight'] == 'down' or \
       controlsStates['ljoySelect'] == 'down':
        asciiColorsStatesChunks[8] = '\033[7m'
    else:
        asciiColorsStatesChunks[8] = ''
    
    # btns Y,A,X,B
    asciiColorsStatesChunks[11] = '\033[7m' if controlsStates['btnY'] == 'down' else ''
    asciiColorsStatesChunks[13] = '\033[7m' if controlsStates['btnA'] == 'down' else ''
    asciiColorsStatesChunks[15] = '\033[7m' if controlsStates['btnX'] == 'down' else ''
    asciiColorsStatesChunks[17] = '\033[7m' if controlsStates['btnB'] == 'down' else ''
    # btns back & start - HIGH by default ( 4.4V on 4.6V )
    asciiColorsStatesChunks[18] = '\033[7m' if controlsStates['btnBack'] == 'down' else ''
    asciiColorsStatesChunks[20] = '\033[7m' if controlsStates['btnStart'] == 'down' else ''
    # keypad up & down - HIGH by default ( 4.4V on 4.6V )
    asciiColorsStatesChunks[10] = '\033[7m' if controlsStates['keypadUp'] == 'down' else ''
    asciiColorsStatesChunks[12] = '\033[7m' if controlsStates['keypadDown'] == 'down' else ''
    

def sourceAsciiController():
    #bashArgs = '"'+'" "'.join( asciiEventStatesChunks )+'"'
    #sourcingCmd = '. ./ascii_controller '+bashArgs
    #os.system( sourcingCmd )
    asciiEventStatesChunks = generateEventStatesURI().rstrip('\n').split('/')
    
    #asciiEventStatesChunks[2] = layoutFormat( asciiEventStatesChunks[2] )
    #asciiEventStatesChunks[3] = layoutFormat( asciiEventStatesChunks[3] )
    #asciiEventStatesChunks[4] = layoutFormat( asciiEventStatesChunks[4] )
    #asciiEventStatesChunks[5] = layoutFormat( asciiEventStatesChunks[5] )
    
    #asciiEventStatesChunks[2] = layoutFormat( str( asciiEventStatesChunks[2] ) )
    #asciiEventStatesChunks[3] = layoutFormat( str( asciiEventStatesChunks[3] ) )
    #asciiEventStatesChunks[4] = layoutFormat( str( asciiEventStatesChunks[4] ) )
    #asciiEventStatesChunks[5] = layoutFormat( str( asciiEventStatesChunks[5] ) )
    
    updateAsciiColorsStatesChunks()
    bashColors = asciiColorsStatesChunks
    #print '[ BASH COLORS: ',bashColors,' ]'
    
    #print 'asciiEventStatesChunks[2], [3], [4] & [5]: ', asciiEventStatesChunks[2], asciiEventStatesChunks[3], asciiEventStatesChunks[4], asciiEventStatesChunks[5]
    asciiEventStatesChunks[2] = '{:>3}'.format( asciiEventStatesChunks[2] )
    asciiEventStatesChunks[3] = '{:>3}'.format( asciiEventStatesChunks[3] )
    asciiEventStatesChunks[4] = '{:>3}'.format( asciiEventStatesChunks[4] )
    asciiEventStatesChunks[5] = '{:>3}'.format( asciiEventStatesChunks[5] )
    #print 'asciiEventStatesChunks[2] formatted:', '{:>3}'.format( asciiEventStatesChunks[2] )
    #print 'asciiEventStatesChunks[2] formatted:', asciiEventStatesChunks[2]
    
    bashArgs = asciiEventStatesChunks
    #generateAsciiURI()
    sourcingCmd = [ 'bash' , './ascii_controller' ]
    bashArgs[:0] = sourcingCmd
    #print bashArgs,'\n'
    bashTestableVersion = './ascii_controller '+'"'+'" "'.join( generateEventStatesURI().rstrip('\n').split('/') )+'"'+'\n'
    #print bashTestableVersion
    
    #bashArgs[-1:] = bashColors
    #bashArgs[-1:] = ['\033[1;37m'] if controlsStates['ltrig'] == 'down' else ['']
    bashArgs.extend( bashColors )
    #print bashArgs
    #bashArgs.extend( ['\x1b[7m'] )
    #print 'ASCII CONTROLLER COMMAND: ',bashArgs
    
    
    #sys.stdout.write( '[ Bash Testable: ' + bashTestableVersion + ']'+'\n' ) 
    #asciiController = subprocess.check_output( [ 'bash' , './ascii_controller', '0', '0', '128', '128', '128' ] )
    asciiController = subprocess.check_output( bashArgs )
    print asciiController
    #return asciiController
    #sys.stdout.write( asciiController )
    #sys.stdout.flush()
    
    #asciiColorsStatesChunks[0] = ''

#--------------------------------------------
# Function to generate the "event states URI" ( wich actually concatenates all the controls states into a string that'll be sent to the uC/Arduino for parsing & further processing )
def generateEventStatesURI():
    #eventStatesURI = read_chunk_H9+"/"+read_chunk_H9
    #eventStatesURI = eventStatesURI+'/'+read_chunk_H9+"/"+read_chunk_H9
    evtStURI = readChunks['C1']+'/'+readChunks['H1']+'/'+readChunks['C2']+'/'+readChunks['H2']+'/'+readChunks['C3']+'/'+readChunks['H3']+'/'+readChunks['C4']+'/'+readChunks['H4']
    evtStURI = evtStURI+'/'+readChunks['C5']+'/'+readChunks['H5']+'/'+readChunks['C6']+'/'+readChunks['H6']+'/'+readChunks['C7']+'/'+readChunks['H7']
    evtStURI = evtStURI+'/'+readChunks['C8']+'/'+readChunks['H8']+'/'+readChunks['C9']+'/'+readChunks['H9']+'/'+readChunks['C10']+'/'+readChunks['H10']
    return evtStURI+'\n'




#--------------------------------------------


# -- pyxhook loop for key processing --
# to be moved as last statement in both keypress & keyrelease events instead of here 
# keypress & keyrelease events handlers are defined below as well as pyxhook setup to handle the keyboard keys


#--------------------------------------------
# initial setup
# init the Arduino serial connection
#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=None)
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=None)
except (OSError, IOError) as e:
    print "' should connect uC/Arduino first ;p !"
    quit()
# suppress nasty init outputs
sys.stdout = open(os.devnull, 'w')
# debug loop counter
loopCntr = 0
os.system( 'stty -echo' )
os.system( 'setterm -cursor off' )
# init pyxhook to handles key press  & key realease events
hookr = pyxhook.HookManager() # create a hook manager
hookr.KeyDown = keyboardKeyPress
hookr.KeyUp = keyboardKeyRelease
hookr.HookKeyboard()
hookr.start()
# restore normal stdout for further processing & usage
sys.stdout = sys.__stdout__
# clean the term
sys.stdout.write("\x1b[2J\x1b[H")

# -------------------------------------------
# infinite loop
#while 1 == 1 : 
running = True
while running:
  # debug
  loopCntr += 1

  #ser.write('0/0/128/128/128/128/1/1/1/0/1/0/1/0/1/0/1/0/1/0\n') # quick debug test
  
  # -- update --
  updateChunks() # updates the chunks based on the control states currently set ( themselves updated by the curent key presses / releases within pyxhook loop )
  
  # -- serial comm --
  ser.write( generateEventStatesURI() ) # write the updated event states URI to the uC/Arduino
  callbackData = ser.readline()
  
  # -- stdout ( terminal ) --
  #print( callbackData )
  # sys.stdout.write( '\r'+ callbackData ) display the serial comm coallback in the terminal
  #sys.stdout.write( 'Loop count: ' + str(loopCntr) + ' |  Callback: ' + callbackData )
  # same as above, in case the uC/Arduino sends back stuff with a linefeed ( '\n' ) & we wanna get rid of it:
  #sys.stdout.write( '\r' + 'TRIG_L state: ' + getControlState( 'ltrig' ) + '| Gen.URI: ' + generateEventStatesURI().rstrip('\n') + '| Loop count: ' + str(loopCntr) + '\n' )
  #sys.stdout.write( '\r' + 'Gen.URI: ' + generateEventStatesURI().rstrip('\n') + '| Loop count: ' + str(loopCntr) + ' |  Callback: ' + callbackData.rstrip('\n') )
  #sys.stdout.write( 'Loop count: ' + str(loopCntr) + ' |  Callback: ' + callbackData.rstrip('\n') )
  #sys.stdout.write( 'GeneratedURI: ' + generateEventStatesURI() )
  #sys.stdout.write( '\r'+ callbackData.rstrip('\n') )
  # sys.stdout.write( '0/0/128/128/128/128/1/1/1/0/1/0/1/0/1/0/1/0/1/0\n' ) # quick debug test
  #sys.stdout.write( generateEventStatesURI() ) # quick debug test
  global xtraSpaces
  #sys.stdout.write( '\r' + 'TRIG_L state: ' + getControlState( 'ltrig' ) + '| Gen.URI: ' + generateEventStatesURI().rstrip('\n') + '| Loop count: ' + str(loopCntr) + xtraSpaces )
  #tcflush( sys.stdout, TCIOFLUSH )
  sys.stdout.write("\x1b[2J\x1b[H")
  
  sourceAsciiController()
  
  sys.stdout.write( 'Loop count: '+str(loopCntr) + ' | ' + visualController() +' uC Callback URI: '+callbackData.rstrip('\n') )
  sys.stdout.flush() #don't store characters in a buffer rather than printing them immediately
  sys.stdout.write( '\nLook Ma, I can write stuff here too without glitches ;D ! \n    .. and on multiple lines ;D' )
  sys.stdout.flush()
  #time.sleep( 0.005 ) # seems to work fine on the Arduino side when just parsing serial& returning corresonding serial without further I/O
  #time.sleep( 2 )
  

#--------------------------------------------
ser.close()
hookr.cancel() # stop hooking ( close the hookr listener when done - aka stop handling keyboard key events )
# restore the terminal normal behavior
os.system( 'stty echo' )
# restore cursor blinking
os.system( 'setterm -cursor on' )

# flush stdin so that once we restore the normal terminal behavior we don't end up with garbage after the prompt - done on key press to avoid increasing garbage
sys.stdout.write( '\n' ) # nevertheless, cleanup the garbage that may be before it
