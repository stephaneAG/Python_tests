# K2000 KIT Python Module
# to be used in conjonction with the arduinoMicroShiftRegisterTest(s), to produce effect(s) such as K2000 KIT
import time
from collections import deque # used to cycle/rotate the leds deck pattern to be sent over serial to the uC/Ar

# == debug tests ==
'''
larger_list = [0,'A','B','C',1, 1,'F','G', 'H', 0]
#print larger_list
smaller_list = larger_list[1:len(larger_list)-1]
#print smaller_list
deck = deque( smaller_list 
#print deck
deck.rotate(1)
#print deck
deck.rotate(-1) # rotate by one to the left
#print deck
'''




config = {
    'large_pattern':  '0000000000',
    'actual_pattern': '00011000',
    'direction':       1,
    'position':        4,
    'deck_len':        2
    #'pattern_len':     len(config['actual_pattern'])
}

def loopOverConfig():
  if config['direction'] == 1:
    print 'direction => RIGHT'
    deckEndIndex = config['position'] + config['deck_len'] - 1
    if deckEndIndex < len(config['large_pattern']):
      # can go right
      print 'free space on right => TRUE'
      large_pattern = config['large_pattern'])
      print 'large pattern as list => '
    else:
      # cannot go right
      print 'free space on right => FALSE'
    
  elif if config['direction'] == 0:
    print 'direction => LEFT'
    if config['position'] > 0:
      # can go left
      print 'free space on left => TRUE'
    else:
      # cannot go left
      print 'free space on left => FALSE'


# == sketch ==
larger_pattern = '0000000000'
pattern = '00011000'
start_direction = 1 # right
start_position = 4 # index of 1st led of the deck
deck_len = 2 # number of leds on at the same time
current_direction = 1 # 1 = right, 0 = left
current_position = 4
current_pattern = '00000000'

# dirty helper function
def loopK200Kit():
  global current_direction
  global current_position
  global larger_pattern
  global current_pattern
  global deck_len
  # could be done: check the mode & its options ( .. )
  
  # check the direction we're set to go to
  if current_direction == 1: # going right
    print 'going right'
    if current_position + deck_len - 1 < len(larger_pattern):
      print 'still free space on the right ..'
      
      large_pattern_list = str(larger_pattern)
      # strip the first & last elements of the list
      sized_pattern = large_pattern_list[1:len(large_pattern_list)-1]
      # convert it to a deque
      deck = deque( sized_pattern )
      
      deck.rotate(1)
      # increment the current position
      current_position += 1
      
      # get back current pattern list from deque
      current_pattern_list = list(deque(deck))
      # write the current pattern as string, not list
      current_pattern = ''.join(current_pattern_list)
      # write the updated larger pattern
      large_pattern = current_pattern_list
      large_pattern[:0] = '0';
      large_pattern[len(large_pattern):] = '0'
      larger_pattern = str( larger_pattern )
      
      # display the current pattern
      print 'pattern: ', current_pattern, ' position: ', current_position
    
    else:
      print 'no more free space on the right ..'
      current_direction = 0
      #return
  
  elif current_direction == 0: #going left
    print 'going left'
    if current_position > 0:
      print 'still free space on the left ..'
      
      large_pattern_list = larger_pattern.split()
      # strip the first & last elements of the list
      sized_pattern = large_pattern_list[1:len(large_pattern_list)-1]
      # convert it to a deque
      deck = deque( sized_pattern )
      
      deck.rotate(-1)
      # decrement the current position
      current_position -= 1
      
      # get back current pattern list from deque
      current_pattern_list = list(deque(deck))
      # write the current pattern as string, not list
      current_pattern = ''.join(current_pattern_list)
      # write the updated larger pattern
      large_pattern = current_pattern_list
      large_pattern[:0] = '0';
      large_pattern[len(large_pattern):] = '0'
      larger_pattern = str( larger_pattern )
      
      # display the current pattern
      print 'pattern: ', current_pattern, ' position: ', current_position
    
    else:
      print 'no more free space on the left ..'
      current_direction = 1
      #return

# infinite loop
while 1 == 1:
  
  loopK200Kit()
  
  time.sleep(2)
  
print 'the program ended'
