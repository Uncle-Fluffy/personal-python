#!/usr/bin/python
# Name of the script - nbassign_robertga
# Purpose -  Creates policies, schedule for Windows client's disk backups in Net# backup
# Date - 09/27/17

print " Hello Customer "

import os, sys, csv
#print os.getcwd()

print(os.getcwd() + "/ssrschedules")


#Open file
path = "/home/robertga/ssrschedules/"
dirs = os.listdir( path )

for file in dirs:
        print file
input_file = raw_input("Enter the filename?")
print "You Answered:", input_file

file_path = path+input_file
print file_path

input_file_object = open(file_path,'r')
for line in input_file_object:
	print line.split()

input_file_object.close()
#print "Handler or Object Variable"

