#!/usr/bin/env python
print "Content-Type: text/plain"
print
import sys
sys.stderr = sys.stdout
f = open('non-existent-file.txt', 'r')
