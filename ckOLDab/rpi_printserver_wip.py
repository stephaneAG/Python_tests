#!/usr/bin/python

# RPI print server v0.0.1a

# import the necessary modules
import fnmatch, os, time # to list files and make use of some OS fcnality (..)
import cgi, cgitb; cgitb.enable() # to use CGI & handle errors as well (..)
from stat import * # to get ST_SIZE ( file size ) & Co (..)
import BaseHTTPServer # to handle the webserver-side of things (..)

class WebRequestHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
	
	# Fcn that handles GET requests
	def do_GET( self ):
		if self.path == '/printserver':
			self.send_response( 200 )
			self.printNormalHeaders() # print the normal HTTP headers
			#self.printAppTop() # prints the App's top ( the end of the actual HTML page )
			self.addStuffToHtmlHead()
			self.printAppInfos()
			self.printFileUploadForm() # print the file upload form to the page
			self.listFilesToDL('.', '*.py') # print a listing of the file currently held by the RPi print server
			self.printFooter()
			#self.printAppBottom() # prints the App's bottom ( the end of the actual HTML page )
		elif self.path == '/CKAB.css':
			self.send_response( 200 )
			self.printFileContent( './CKAB.css' ) # provide the CSS file content
		#elif self.path == '/*.py':
		elif fnmatch.fnmatch( self.path, '/*.py' ):	
			self.send_response( 200 )
			self.printFileHeaders()
			#self.wfile.write('Here will stand the content of the file requested ! : %s' % self.path )
			# get tha name of the file from the path
			theFileName = self.path.replace('/', '')
			self.printFileContent( theFileName )	
		else:
			self.send_error( 404 )
	
	# Fcn that handles GET requests
	def do_POST( self ):
		if self.path == '/save_uploaded_file.py' or self.path == '/rpi_printserver.py' :
			self.send_response( 200 )
			print 'RPIprintserver -> file upload requested and self.path = %s' % self.path # gets triggred -> seems that the form is correctly handled
			
			# handle the file upload process & set the necessary stuff for its successfull completion
			#form = cgi.FieldStorage() # create an instance of the cgi.FieldStorage (..)
			#fileitem = form['file'] # use it to hold the file
			#theForm = cgi.FieldStorage
			theForm = cgi.FieldStorage(keep_blank_values=1)
			#aTest = theForm['file'].value
			aTest = theForm['dummytxt']
			print 'TEST -> dummytxt value: %s' % aTest
			theFile = theForm.getfirst('file', 'empty') # check if anything with that particular key is found .. and if so, get the 1st one
			print 'file found: %s' % theFile
			
			#if fileitem.filename: # check if the file was uploade and act accrodingly if so (..)
   			#	fn = os.path.basename(fileitem.filename) # strip leading path from file name to avoid directory traversal attacks
   			#	open('models/' + fn, 'wb').write(fileitem.file.read()) # write the file in the 'models' directory wich is itself present in the current directory
			#	message = 'The file "' + fn + '" was uploaded successfully' # print a message in case of successfull upload
			#else:
			#	message = 'No file was uploaded' # f*** !
			
			## DEBUG ##
			message = 'this is a dumb message ..'
			self.printNormalHeaders() # print the normal HTTP headers
			self.wfile.write('\n')
			self.wfile.write( message )
			
			
			# show something on page after any try to uploading a file	
			#print """\
			#Content-Type: text/html\n
			#<html><body>
			#<p>%s</p>
			#</body></html>
			#""" % (message,)
				
		else:
			self.send_response( 200 )
			print 'RPIprintserver -> file upload requested and self.path = %s' % self.path
			
			#theForm = cgi.FieldStorage()
			theForm = cgi.FieldStorage(keep_blank_values=1)
			#aTest = theForm['file'].value
			aTest = theForm['dummytxt']
			print 'TEST -> dummytxt value: %s' % aTest
			theFile = theForm.getfirst('file', 'empty') # check if anything with that particular key is found .. and if so, get the 1st one
			print 'file found: %s' % theFile
			
			## DEBUG ##
			message = 'this is a dumb message ..'
			#self.printNormalHeaders() # print the normal HTTP headers
			self.printFileHeaders()
			self.wfile.write('\n')
			self.wfile.write( message )
			
	
	# Fcns that generates the necessary headers	
	def printNormalHeaders( self ):
		#print 'Hello CKAB World!'
		# send the headers
		self.send_header( 'Content-type', 'text/html' )
		# end the headers
		self.end_headers()
		self.wfile.write("\n")
		#self.wfile.write("Hello CKAB index!")
		
	def printFileHeaders( self ):
		print 'RPIprintserver -> a file has been requested'
		#send the headers
		self.send_header('Content-type', 'application/octet-stream')
		# end the headers
		self.end_headers()
		self.wfile.write('\n')
		
		## WIP DEBUG TEST ##
		theActualForm = cgi.FieldStorage()
		theActualFile = theActualForm.getfirst('file', 'empty') # check if anything with that particular key is found .. and if so, get the 1st one
		print 'file found: %s' % theActualFile

	# Fncs that handle specific stuff (..)
	def listFilesToDL( self, theDirectory, theFileType ):
	        print 'generating <li>\'s ..'
	        for file in os.listdir( theDirectory ): # ex: for root -> theDirectory = '/' , current -> '.', etc (..)
	                if fnmatch.fnmatch( file, theFileType ): # ex: for txt's -> theFiletype = '*.txt', ogg -> '*.ogg', etc (..)
       	                	# try to get some infos about the file
                        	try:
                        	        st = os.stat( file )
                        	except IOERROR:
                        	        print 'failed to get infos about', file
                        	else:
                        	        theFileSize = st[ ST_SIZE ]
                        	        theFileLastMod = time.asctime( time.localtime( st[ ST_MTIME ] ) )
                        	        print '<li class="file-to-dl">', file, ' | added on: ', theFileLastMod, ' | size: ', theFileSize, '<a href="file:////Users/stephaneadamgarnier/CKAB/python_webdev/"', file, '"> Download </a> </li>'
                        	        # write the content to the response socket (..)
                        	        self.wfile.write( '<li class="file-to-dl">' )
					self.wfile.write( file, )
					self.wfile.write( ' | added on: ' )
					self.wfile.write( theFileLastMod )
					self.wfile.write( ' | size: ' )
					self.wfile.write( theFileSize )
					#theFilePath = os.path.abspath( '%s/%s' % (theDirectory, file) )
					self.wfile.write( '<a href="./%s"' % file ) # self.wfile.write( '<a href="%s"' % theFilePath ) # self.wfile.write( '<a href="file:///Users/stephaneadamgarnier/CKAB/python_webdev/%s"' % file )
					self.wfile.write( '> Download ! </a>     <a href=""> Build! </a> </li>' )
					self.wfile.write( '\n')
	def printFileContent ( self, theFile ):
		fo = open( theFile, 'r+' ) # open the file for reading
		theFileContent = fo.read() # read the entire file content
		self.wfile.write( theFileContent ) # write the file content to the page
		fo.close() # close the file after doing sutff with it	
	
	# Fncs that handles printing the usual HTML stuff
	#def printAppTop( self ):
		#self.wfile.write( '<html><head><title> RPi print server </title></head>' ) # page start
		#self.wfile.write( '<body>' ) # body start
	
	# Fcn that handles printing the usual HTML stuff as well
	#def printAppBottom( self ):
		#self.wfile.write( '</body></html>' ) # body end
	
	# Fcn that prints the HTML page footer
	def printFooter( self ):
		self.wfile.write( '\n\n' )
                self.wfile.write( '<div class="footer"> cc RPI print server | CKAB - 2013 </div>' )
	# Fcn that prints infos about the RPi print server
	def printAppInfos( self ):
		self.wfile.write( '<div class="company-title"> <h1>CKAB</h1> </div> ' )
		self.wfile.write( '<div class="app-title"> <p>RPi print server</p> </div>' )
		self.wfile.write( '<div class="server-infos">' )
		self.wfile.write( '<p> Server version: %s </p>' % self.server_version )
		self.wfile.write( '<p> System version: %s </p>' % self.sys_version )
		self.wfile.write( ' </div>' )
	
	# Fcn that append the necessary Javascript & CSS stuff to the HTML HEAD of the page 
	def addStuffToHtmlHead( self ):
		self.wfile.write( '<html><head><title> RPi print server </title>' )
		self.wfile.write( '<script type="text/javascript"> alert("Hello CKAB world!") </script>' )
		self.wfile.write( '<link rel="stylesheet" type="text/css" href="./CKAB.css" />' )	
		self.wfile.write( '</head>' )
		
	# Fcn that prints a form for file upload
	def printFileUploadForm( self ):
		#self.wfile.write( '<form class="file-upload-form" enctype="multipart/form-data" method="post" action="rpi_printserver.py">' ) # previously 'save_uploaded_file.py'
		self.wfile.write( '<form class="file-upload-form" enctype="multipart/form-data" method="post">' ) # prints -> ' RPIprintserver -> file upload requested and self.path = /printserver '
		self.wfile.write( '<p> Upload a file: <input type="file" name="file" /> </p>' ) #self.wfile.write( '<p> Upload a file: <input type="file" name="file"> </p>' )
		self.wfile.write( '<p> Enter dummy text: <input type="text" name="dummytxt" value="Hello there"> </p>' )
		self.wfile.write( '<p> <input type="submit" value="Upload!"> </p>' )
		self.wfile.write( '</form>' )
		
server = BaseHTTPServer.HTTPServer( ('127.0.0.1', 80), WebRequestHandler )
print 'RPI printserver started on port 80 ..'
server.serve_forever()


