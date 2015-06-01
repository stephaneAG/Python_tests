#!/bin/bash

# quick & ditry test to see if "We/I can make this particular bear dance [again]" ;D
#
# Nb: digg the following for maybe a way to know wich keys are currently pressed ( aka more than one at a time -> better to update our event states URI ;p )
# http://superuser.com/questions/248517/show-keys-pressed-in-linux
# also
# http://stackoverflow.com/questions/9731281/bash-script-listen-for-key-press-to-move-on
# &
# http://stackoverflow.com/questions/23462221/bash-read-input-only-once-and-do-not-continue-reading-until-key-is-released


# --------------------------------------------
# Source used aliases & fcns
source ~/.bash_stephaneag_functions
source ~/.bash_stephaneag_aliases

# --------------------------------------------
# trap ctrl-c and call ctrl_c() ( useful for cleanup )
trap ctrl_c INT

ctrl_c() {
  #echo
  #echo "** Trapped CTRL-C ! **"
  # do some cleanup
  cleanup

  # fix to restore the prompt ( ' having invisible commands typing, because "read" disbles local echo ( .. ) )
  #reset - as efficient but has side effects :/
  stty "$console_bckp"
  
  exit 0
}

#--------------------------------------------
# cleanup
cleanup(){
  # delete file descriptor used for the Arduino serial conn, aka close /dev/ttyUSB0
  exec 3>&-

  echo -en "\rcleanup done!"
}


#--------------------------------------------
# Arduino event states URI chunks -> those will be updated & used a the event states URI chunks, & also allows us to have the needed defaults in our URI
read_chunk_C1="0"   # chunk #1  ( ltrig )
read_chunk_H1="0"   # chunk #2  ( rtrig )
read_chunk_C2="128" # chunk #3  ( ljoyY )      / resting voltage 2.3V on 4.6V
read_chunk_H2="128" # chunk #4  ( rjoyY )      / resting voltage 2.3V on 4.6V
read_chunk_C3="128" # chunk #5  ( ljoyX )      / resting voltage 2.3V on 4.6V
read_chunk_H3="128" # chunk #6  ( rjoyX )      / resting voltage 2.3V on 4.6V
read_chunk_C4="1"   # chunk #7  ( ljoyS )      / HIGH by default ( 4.4V on 4.6V )
read_chunk_H4="1"   # chunk #8  ( rjoyS )      / HIGH by default ( 4.4V on 4.6V )
read_chunk_C5="1"   # chunk #9  ( btnBack )    / HIGH by default ( 4.4V on 4.6V )
read_chunk_H5="0"   # chunk #10 ( btnBlack )
read_chunk_C6="1"   # chunk #11 ( btnStart )   / HIGH by default ( 4.4V on 4.6V )
read_chunk_H6="0"   # chunk #12 ( btnWhite )
read_chunk_C7="1"   # chunk #13 ( keypadUp )   / HIGH by default ( 4.4V on 4.6V )
read_chunk_H7="0"   # chunk #14 ( btnY )
read_chunk_C8="1"   # chunk #15 ( keypadDown ) / HIGH by default ( 4.4V on 4.6V )
read_chunk_H8="0"   # chunk #16 ( btnA )
read_chunk_C9="1"   # chunk #17 ( keypadLeft ) / HIGH by default ( 4.4V on 4.6V )
read_chunk_H9="0"   # chunk #18 ( btnX )
read_chunk_C10="1"  # chunk #19 ( keypadRight ) / HIGH by default ( 4.4V on 4.6V )
read_chunk_H10="0"  # chunk #20 ( btnB )


#--------------------------------------------
# No need to specify control defaults ( & neither keyup events ) as they're automatically reset at the beginning of each loop on the uC side

#--------------------------------------------
# Analog controls defaults & range to be used in arithmetical expressions responsible for smoothing - not currently used
# chunk #1  ( ltrig )
ltrig_min=0
ltrig_max=255
curr_ltrig=0
# chunk #2  ( rtrig )
ltrig_min=0
ltrig_max=255
curr_ltrig=0

# chunk #3  ( ljoyY )      / resting voltage 2.3V on 4.6V
ljoyY_min=0
ljoyY_max=255
curr_ljoyY=128
# chunk #4  ( ljoyX )      / resting voltage 2.3V on 4.6V
ljoyY_min=0
ljoyY_max=255
curr_ljoyY=128
# chunk #6  ( rjoyY )      / resting voltage 2.3V on 4.6V
ljoyY_min=0
ljoyY_max=255
curr_ljoyY=128
# chunk #7  ( rjoyX )      / resting voltage 2.3V on 4.6V
ljoyY_min=0
ljoyY_max=255
curr_ljoyY=128


#--------------------------------------------
# Keyboard keys default states ( mapped with the name of their control )
state_ltrig="up"
state_rtrig="up"
state_ljoyUp="up"
state_ljoyDown="up"
state_ljoyLeft="up"
state_ljoyRight="up"
state_ljoySelect="up"
state_btnY="up"
state_btnA="up"
state_btnX="up"
state_btnB="up"
state_btnBack="up"
state_btnStart="up"
state_keypadUp="up"
state_keypadDown="up"


#--------------------------------------------
# Simple arithmetical expressions & stuff ( maybe to be used later with AAF for a character control on a map ? ;P )
x=0
x_max=100 # screen width
y=0
y_max=50 # screen height
curr_x=50
curr_y=25

zoom=0
zoom_max=100
curr_zoom=50



#--------------------------------------------
# Functions using arithmetical expressions to update curr_x & curr_y, and also curr_zoom ;) - not currently used, kept from older code ( .. )
upKeyPress(){
  if (( "$curr_x" >= "$x_max" )); then
    curr_x="$x"
  else
    let curr_x++
  fi
}
downKeyPress(){
  if (( "$curr_x" <= "$x" )); then
    curr_x="$x_max"
  else
    let curr_x--
  fi
}
leftKeyPress(){
  if (( "$curr_y" <= "$y" )); then
    curr_y="$y_max"
  else
    let curr_y--
  fi
}
rightKeyPress(){
  if (( "$curr_y" >= "$y_max" )); then
    curr_y="$y"
  else
    let curr_y++
  fi
}


#--------------------------------------------
# Key event listener - used to check if keys other than the one just pressed are already down & generate eventStatesURI accordingly before sending it to the uC
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
handleOtherKeys(){
  # get the keys state ( either up or down )
  state_ltrig=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[53]=" | cut -d "=" -f2)
  state_rtrig=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[57]=" | cut -d "=" -f2)
  state_ljoyUp=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[41]=" | cut -d "=" -f2)
  state_ljoyDown=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[55]=" | cut -d "=" -f2)
  state_ljoyLeft=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[40]=" | cut -d "=" -f2)
  state_ljoyRight=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[42]=" | cut -d "=" -f2)
  state_ljoySelect=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[27]=" | cut -d "=" -f2)
  state_btnY=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[111]=" | cut -d "=" -f2)
  state_btnA=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[116]=" | cut -d "=" -f2)
  state_btnX=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[113]=" | cut -d "=" -f2)
  state_btnB=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[114]=" | cut -d "=" -f2)
  state_btnBack=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[30]=" | cut -d "=" -f2)
  state_btnStart=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[31]=" | cut -d "=" -f2)
  state_keypadUp=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[32]=" | cut -d "=" -f2)
  state_keypadDown=$(xinput query-state "AT Translated Set 2 keyboard" | grep "key\[33]=" | cut -d "=" -f2)

  # depending on up or down, adjust the corresponding chunk
  # triggers
  if [[ "$state_ltrig" == "down" ]]; then read_chunk_C1="1"; else read_chunk_C1="0"; fi
  if [[ "$state_rtrig" == "down" ]]; then read_chunk_H1="1"; else read_chunk_H1="0"; fi
  # left joystick Y - resting voltage 2.3V on 4.6V
  if [[ "$state_ljoyUp" == "down" && "$state_ljoyDown" == "up" ]]; then 
    read_chunk_C2="255"; # go upward
  elif [[ "$state_ljoyDown" == "down" && "$state_ljoyUp" == "up" ]]; then
    read_chunk_C2="0"; # go backward
  else
    read_chunk_C2="128"; # stay still
  fi
  # left joystick X - resting voltage 2.3V on 4.6V
  if [[ "$state_ljoyLeft" == "down" && "$state_ljoyRight" == "up" ]]; then 
    read_chunk_C3="0"; # go left
  elif [[ "$state_ljoyRight" == "down" && "$state_ljoyLeft" == "up" ]]; then
    read_chunk_C3="255"; # go right
  else
    read_chunk_C3="128"; # stay still
  fi
  # left joystick select - HIGH by default ( 4.4V on 4.6V )
  if [[ "$state_ljoySelect" == "down" ]]; then read_chunk_C4="0"; else read_chunk_C4="1"; fi
  # btns Y,A,X,B
  if [[ "$state_btnY" == "down" ]]; then read_chunk_H7="1"; else read_chunk_H7="0"; fi
  if [[ "$state_btnA" == "down" ]]; then read_chunk_H8="1"; else read_chunk_H8="0"; fi
  if [[ "$state_btnX" == "down" ]]; then read_chunk_H9="1"; else read_chunk_H9="0"; fi
  if [[ "$state_btnB" == "down" ]]; then read_chunk_H10="1"; else read_chunk_H10="0"; fi
  # btns back & start - HIGH by default ( 4.4V on 4.6V )
  if [[ "$state_btnBack" == "down" ]]; then read_chunk_C5="0"; else read_chunk_C5="1"; fi
  if [[ "$state_btnStart" == "down" ]]; then read_chunk_C6="0"; else read_chunk_C6="1"; fi
  # keypad up & down - HIGH by default ( 4.4V on 4.6V )
  if [[ "$state_keypadUp" == "down" ]]; then read_chunk_C7="0"; else read_chunk_C8="1"; fi
  if [[ "$state_keypadDown" == "down" ]]; then read_chunk_C8="0"; else read_chunk_C8="1"; fi
  
  # we already have the defaults for the ones we're not using: H2,H3,H4,H5,H6,C9,C10
  
  # generate the even states URI to be sent to the uC / Arduino
  eventStatesURI="$read_chunk_C1/$read_chunk_H1/$read_chunk_C2/$read_chunk_H2/$read_chunk_C3/$read_chunk_H3/$read_chunk_C4/$read_chunk_H4/$read_chunk_C5/$read_chunk_H5"
  eventStatesURI="$eventStatesURI/$read_chunk_C6/$read_chunk_H6/$read_chunk_C7/$read_chunk_H7/$read_chunk_C8/$read_chunk_H8/$read_chunk_C9/$read_chunk_H9"
  eventStatesURI="$eventStatesURI/$read_chunk_C10/$read_chunk_H10"
  
  # get anything present in the serial conn from the uC ( "booted" or an event states URI ) - working from here but seems slow :/
  #arduino_eventStatesURI=$(cat <&3)
  
  # send the event states URI to the uC / Arduino
  # ex: echo "0/0/128/128/128/128/1/1/1/0/1/0/1/0/1/0/1/0/1/0" >&3
  echo "$eventStatesURI" >&3
  
  # get anything present in the serial conn from the uC ( "booted" or an event states URI )
  arduino_eventStatesURI=$(cat <&3)
}


#--------------------------------------------
# Event states URI logging
# the following is the default uC callback received from serial for an input like the first line following
# 0/0/128/128/128/128/1/1/1/0/1/0/1/0/1/0/1/0/1/0
arduino_eventStatesURI="ltrig:0/rtrig:0/ljoyY:128/rjoyY:128/ljoyX:128/rjoyX:128/ljoyS:1/rjoyS:1/back:1/black:0/start:1/white:0/up:1/Y:0/down:1/A:0/left:1/X:0/right:1/B:0"
logEventStates(){
  echo -en "\rARDUINO CALLBACK: [ $arduino_eventStatesURI ]"
}


#--------------------------------------------
# Hacky handling of arrow keys ( using "A"(up), "B"(down), "D"(left), "C"(right))
hackyKeyboardHandle(){
  # fix to prevent previous lines from appearing ( contains more spaces than the most wide stuff echoed, nb: better ? -> cursor ( AAF ) )
  echo -en "\r                                                                                                                                                                   "
  case $key in
  # x) ltrigPress ;; # LTRIG
  # n) rtrigPress ;; # RTRIG
  # f) ljoyUp ;; # LJOY UP
  # v) ljoyDown ;; # LJOY DOWN
  # d) ljoyLeft ;; # LJOY LEFT
  # g) ljoyRight ;; # LJOY RIGHT
  # r) ljoySelect ;; # LJOY SELECT
  # A) btnYPress ;; # BTN Y
  # B) btnAPress ;; # BTN A
  # D) btnXPress ;; # BTN X
  # C) btnBPress ;; # BTN B
  # u) btnBackPress ;; # BTN BACK
  # i) btnStartPress ;; # BTN START
  # o) keypadUpPress ;; # KEYPAD UP
  # p) keypadUpPress ;; # KEYPAD DOWN
  q) ctrl_c ;; # quit ( same as Ctrl+C )
  # *) logInfos $key # helpful for debugging
  esac
 
  # also take in account other keys that may already be pressed - kinda hacky, but I guess it'll work ;D
  handleOtherKeys
   
  # todo: send the event states URI to the uC
  
  # to do: get the event states URI callback & update it locally
  
  # log either the default infos or actual infos updated after getting a serial callback from the Arduino
  logEventStates
  
}

#--------------------------------------------
#Init & args debug

# fix to restore the prompt ( see code in trap Ctrl-C )
console_bckp=$(stty -g)

# TODO: init the arduino serial conn & hackety trick
exec 3<> /dev/ttyUSB0
# wait for Arduino's initialization
sleep 1


#--------------------------------------------
# Automation -> if we're passed an automation script, we should source it instead of runnig an infinite loop to get the user's controls
# the so-colled automation script is 
automation_path_arg="$1"
echo "AUTOMATION PATH PASSED AS ARG: $automation_path_arg"


#--------------------------------------------
# Infinite loop
while true
do
  read -s -n1 key # Read 1 characters.
  #echo -en "\rREAD: [" $key "]"
  hackyKeyboardHandle
done
