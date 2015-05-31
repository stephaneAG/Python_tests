#!/usr/bin/python

#impoer the necessary modules
import re # the regexp module

# listen command test python file


# // THE FCNS //

# the fcn that iterate through the recognized command list to find a match with the received pseech command
def listenForCommand( theCommand ):
	#for s in range( len( cmdsList ) ):
	for k in commandsParams.items():
		# hold the current 'loop[i]' to rung the matching process against it
		#matchingCmd = re.search(r cmdsList[i], theCommand )
		matchingCmd = re.search(r"say hello", theCommand )
		
		# check if the match was successfull and end the iteraction / handle it
		if matchingCmd:
			print "Matching command found:"
			print matchingCmd
			print "Associated function:"
			#print fcnsList[s]
			# end the iteration as we found the command
			break
		
		else:
			# continue to loop until 'cmdsList' has been fully iterated over (..)


# the settings ( commands recognized ans associated functions )
cmdsList = ["say hello", "repeat after me", "do the cleaning", "do my work"] # IndentationError: expected an indented block
fcnsList = ['sayHello', 'repeatAfterMe', 'doTheCleaning', 'doMyWork']

commandsParams = {"say hello" : "sayHello", "repeat after me" : "repeatAfterMe", "do the cleaning" : "doTheCleaning", "do my work" : "doMyWork"} # this is a dictionary






# // THE PRGM //

print "\n PRGORAM BEGIN \n"

# fake received speech on wich we iterate to find a matching command
receivedCmd = "say hello"

# try to find a match with a fake command
listenForCommand( receivedCmd )
