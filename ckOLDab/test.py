#!/usr/bin/python

# RPI print server v0.0.1a

# import the necessary modules
import fnmatch, os, time # to list files and make use of some OS fcnality (..)
from stat import * # to get ST_SIZE ( file size ) & Co (..)
import BaseHTTPServer # to handle the webserver-side of things (..)


# the Fcns definitions

# a Fcn that prints an <li> for each file found in a given directory
def printFilesLIs( theDirectory, theFileType ):
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
				return '<li class="file-to-dl">', file, ' | added on: ', theFileLastMod, ' | size: ', theFileSize, '<a href="file:////Users/stephaneadamgarnier/CKAB/python_webdev/"', file, '"> Download </a> </li>', '\n'

class WebRequestHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
	def do_GET( self ):
		if self.path == '/printserver':
			self.send_response( 200 )
			self.do_stg()
		else:
			self.send_error( 404 )
	
	def do_stg( self ):
		print 'Hello CKAB World!'
		# testing ..
		# send the headers
		self.send_header( 'Content-type', 'text/html' )
		# end the headers
		self.end_headers()
		self.wfile.write("\n")
		self.wfile.write("Hello CKAB index!")
		# make use of our Fcn that produces LIs from files with specific extensions in the folder of our choice
		self.wfile.write( printFilesLIs( '.', '*.py' ) )
		#print the "minimalistic footer"
		self.wfile.write( '\n' )
		self.wfile.write( 'cc RPI print server | CKAB - 2013' )

server = BaseHTTPServer.HTTPServer( ('127.0.0.1', 80), WebRequestHandler )
print 'RPI printserver started on port 80 ..'
server.serve_forever()


