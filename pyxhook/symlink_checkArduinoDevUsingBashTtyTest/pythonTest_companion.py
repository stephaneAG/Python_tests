import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=None)

#while True:
while 1 == 1 : 
  ser.write('0/0/128/128/128/128/1/1/1/0/1/0/1/0/1/0/1/0/1/0\n')
  callbackData = ser.readline()
  print( callbackData )
  time.sleep( 0.005 )
  #bytesToRead = ser.inWaiting()
  #print ser.read(bytesToRead)
  print "One second just elapsed ! .."
  
ser.close()

#import serial
#>>> import io
#>>> ser = serial.serial_for_url('/dev/ttyUSB0', timeout=2)
#>>> sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
#>>> sio.write(unicode("0/0/128/128/128/128/1/1/1/0/1/0/1/0/1/0/1/0/1/0\n"))
#48L
#>>> sio.flush() # it is buffering. required to get the data out *now*
#>>> hello = sio.readline()
#>>> print hello == unicode("hello\n")
#False
#>>> print hello
#ltrig:0/rtrig:0/ljoyY:128/rjoyY:128/ljoyX:128/rjoyX:128/ljoyS:1/rjoyS:1/back:1/black:0/start:1/white:0/up:1/Y:0/down:1/A:0/left:1/X:0/right:1/B:0
