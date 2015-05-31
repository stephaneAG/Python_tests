#StephaneAG - 2012

#simple chat server for iphone socket communication using python
# to run : sudo Python iphone_chat_server.py # > Using sudo as it requires administer access to listen on a port on the machine

# to test : telnet localhost 80

# Chat events: >we use a simple format to exchange messages : strings separated by a ":" . Before that char we have the command, wican be "iam" or "msg"
	# the "iam" msg is used when someone joins the chat and is followed by a nickname of who joined the chat
	# the "msg" comd sends a message to all clients. There is no need for "msg" to carry the name of the sender, because it is managed server side, in the self.factory.client.list
	
	# > We do not need to use simple string-based protocols, we can use JSON, XML , custom binary format, or whatever we like ;p



#from twisted.internet.protocol import Factory,  # factory mthd : creates a management machinery to handle connection established with clients
from twisted.internet.protocol import Factory, Protocol # import Protocol plus factory stuff
from twisted.internet import reactor #importing the reactor files

## defining a protocol ##
# > The protocol is exactly the logic of the server application. This is were we state what to do when a client connects, sends msg, and so on ..

# class IphoneChat(Protocol): # creation of new class "IphoneChat" that extends "Protocol"
# 	def connectionMade(self): # and extends the "connectionMade" hook that prints a msg when a connection is made
# 		print "a client connected"

##
## modified version to keep track of clients: Each client has a socket assigned, so we need t ostore that info in an array
##

class IphoneChat(Protocol): # creation of new class "IphoneChat" that extends "Protocol"
	def connectionMade(self): # and extends the "connectionMade" hook that prints a msg when a connection is made
		self.factory.clients.append(self)
		print "clients are ", self.factory.clients
		
	def connectionLost(self, reason): # managing a user disconnection ( > connectionLost callback ) "for the Sake of Completeness"
		self.factory.clients.remove(self)
		
	def dataReceived(self, data): # TO RECEIVE DATA, THE CALLBACK WE HAVE TO OVERRIDE HAS THE PREVIOUS SIGNATURE. > in this callback , data is received by the socket
		a = data.split(':') # Split the string to find out the command
		print a
		if len(a) > 1:
			command = a[0] #  holds the first part of the splitted string
			content = a[1] #  holds the second part of the splitted string
			
			msg = "" # empty (for the moment) message
			if command == "iam": # if the cmd is "iam"
				self.name = content # store the name of the client
				msg = self.name + " has joined" # alert user joined
				#print msg # build the custom message ##WAS NOT WRITTEN IN THE TUT > TESTING
				
			elif command == "msg": # if the cmd is "msg"
				msg = self.name + ": " + content # store the msg of the client + his name
				print msg # build the custom message
				
			for c in self.factory.clients:
				c.message(msg) # broadcast the message to all clients ## use the "message" mthd right below
				
	def message(self, message): # "message" mthd implm
		self.transport.write(message + '\n') # IMPORTANT : use of the '\n' char so the socket detects when the message transmission has completed.

factory = Factory() # the factory handles connections

##
## added to to keep track of clients
factory.clients = [] # initialise the array of clients as empty right after the line creating the factory
##

#assign our class as the protocol of our factory
factory.protocol = IphoneChat # assign IphoneChat protocol to factory

reactor.listenTCP(80, factory) # implementation of a reactor pattern 
	# > Uses port 80 cuz open by default ( as standard port for http conns)
	# > allow real-device-app testing wirelessly without modifying settings of the router
	
print "Iphone Chat Server Started"

reactor.run() # run the server
