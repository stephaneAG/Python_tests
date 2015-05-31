from sys import argv # import the necessary features for our python script (in that particular case, stg to handle command-line arguments)

script, firstArg, secondArg, thirdArg = argv # 'unpacks' the arguements from the cmd-line to be held in their respective variables 

print "Script is called:", script
print "first variable passed:", firstArg
print "second variable passed:", secondArg
print "third variable passed:", thirdArg
