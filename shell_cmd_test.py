import subprocess

subprocess.call(['say', ' Hello World from Python.'])

listing_holder = subprocess.call(['ls','-l'])
if listing_holder > 0:
	print "here the files listing resulting from the shell command ran from within python: \n %s" %listing_holder
