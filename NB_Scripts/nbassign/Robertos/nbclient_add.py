#!/usr/bin/python
# Name of the script - nbclient_add.py
# Created by - Roberto Garcia
# Purpose -  Creates policies, schedule for Windows client's disk backups in Net# backup
# Date - 09/27/17

print " Hello Customer "

import os, sys, csv, re, shlex, subprocess

print(os.getcwd() + "/ssrschedules")


#Open file
path = "/home/robertga/ssrschedules/"                  #Location where csv file resides.
dirs = os.listdir( path )

for file in dirs:
        print file
input_file = raw_input("Enter the filename?")          #User input request, select csv file your going to be using.
print "You Answered:", input_file

file_path = path+input_file
print file_path

input_file_object = open(file_path,'r')                #Opens and reads file in the given path.
for line in input_file_object:
        if re.match("Free",line):
                pass
        else:
                line_data = line.split(",") #Splits the colums we are searching for by comman.
		cmd = "/usr/openv/netbackup/bin/admincmd/bpplclients tvp01stor20_nbu_images -M tvp02nbadm01 -add %s-nfs Windows Windows" % (line_data[0])    #NB command to add clients to backup policy.
		args = shlex.split(cmd) #Shlex allows to read the spaces on the cmd line.
		print cmd
		print args	
		output,error=subprocess.Popen (args,stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
		print output,error

input_file_object.close()


