# to run : ' python ex15.py ex15_sample.txt '

from sys import argv

script, filename = argv

txt = open(filename) # creates a file object

print "Here, the content of the file %r:" % filename
print txt.read() # read from the file object

txt.close()
