#!/usr/bin/python

#import the necessary modules
import re # the regexp module



# define the necessary fcns
def lookForCmd( theCommand ):
	for commandIndex, commandAgainst in enumerate( commandsToMatchList ): # works > but the above is used to fetch the index AND the item (..)
	#for commandAgainst in commandsToMatchList: # works > but the above is used to fetch the index AND the item (..)
		
		#possibleMatch = re.search(r"%s" % commandToMatch, text) # works ?
		possibleMatch = re.search(r"%s" % commandAgainst, theCommand) # works ?
		
		# check if the match was successfull and end the iteraction / handle it
		if possibleMatch:
			print "Matching command found:"
			print theCommand
			print "Matching command index"
			print commandIndex
			print "Associated function:"
			print commandsAssociatedFcnsList[commandIndex]
			# end the iteration as we found the command
			#break
		
		else:
			# continue to loop until 'cmdsList' has been fully iterated over (..)
			print "Matching command not found at this entry index"





text = "Hello world from the Tef"
commandToMatch = "Hello (.*) from the Tef"

#match = re.search(r"Hello (.*) from the Tef", text) # works > finds it
match = re.search(r"%s" % commandToMatch, text) # works > finds it

if match:
	print "found!"
else:
	print "not found"
	
	
commandsToMatchList = [ "Hello (.*) from the Tef", "Do (.*) I tell you to", "Suck (.*) dummy!"]
commandsAssociatedFcnsList = [ "HelloFromTef()", "DoIt", "suckMyBalls"]

print commandsToMatchList # work > simply prints out the lists of recognized commands

print "\n"

lookForCmd( text )

