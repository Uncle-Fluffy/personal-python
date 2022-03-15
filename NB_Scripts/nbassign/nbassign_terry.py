#!/usr/bin/python
# nbassign_terry
# tscarter

# This script scrapes an input .csv file, 
#	reads it line by line,
#	picks out the parts we need
#	determines the host name, the time for full backukps and day of week
#	determines what policy to use
#	formats the output of the assign command, the host name and policy
# Sept 27, 2017

#init
import subprocess
file_location = "/home/tscarter/ssrschedules"

print "Hello World"
print
subprocess.call (["ls", "-l", file_location])

print

input_file = raw_input("File Name?: ")
print "You typed: ", input_file
input_file_fullpath = file_location + "/" + input_file
print input_file_fullpath
print

input_file_object = open(input_file_fullpath,"r")

#print input_file_object.readline()

for line in input_file_object:
#  print line,
#  print ("line is of type ", type(line))
  line_parts = line.split(",")
  if "Free" not in line_parts[0]:
    print line_parts[0],line_parts[2],line_parts[3],line_parts[10]
input_file_object.close()

#end
