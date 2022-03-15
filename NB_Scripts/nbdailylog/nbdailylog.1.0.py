#!/usr/bin/python
# nbdailylog.py
Version = 1.0
#
# Author: Terry Carter
#
# v 1.0 9/20/2019 Creation
#

############################################################################################
#
#  Init
# Here are all of the things needed to initialize the processes used.
#
############################################################################################

from epoch_time import this_morning                     # This morning formatted in epoch time
from epoch_time import yesterday_morning                # Yesterday morning formatted in epoch time
from epoch_time import epoch_to_date                    # Convert the epoch back to a human date
from epoch_time import single_string_date               # Get the date as a single string
from nbjobs import scrape_most as scrape                # gets nb job information

import subprocess                                       # Used for Popen, directions to the command line

import socket                                           # Used to get host information
Hostname = socket.gethostname()                         # Get host name
MailTo = "terry.carter@oracle.com"                      # Names of people to send this report to
HostFolder = "/usr/openv/scripts/logs/nbud/"            # Where to stick the daily logs


############################################################################################
#
# Report File Name
#
############################################################################################

def report_file_name():
    return "nbud_" + single_string_date() + "_" + Hostname


############################################################################################
#
#  Gather Jobs
#
############################################################################################

def gather_jobs(ReportFileName):                        # Grab the jobs finished yesterday
    today_epoch_time = this_morning()                   # Get this morning's epoch time
    yesterday_epoch_time = yesterday_morning()          # Get yesterday morning's epoch time
    raw_jobs = scrape()                                 # Get a list of NBU jobs
    job_array = []                                      # Initialize array
    with open(ReportFileName,'w') as ReportFile:        # Open the file in write mode

        for line in raw_jobs.splitlines():              # Look through every job
            field = line.split(",")                     # Split every field in the line
            if (int(field[10]) >= yesterday_epoch_time) and (int(field[10]) < today_epoch_time):      # Job finished yesterday
#                print line
                ReportFile.write(line + "\n")           # Write the line to the report file


############################################################################################
#
#  SendEmail
# Send a mail the the recipients with the previously formatted body
#
# Input: None
# Output: Mail - File 'ReportFileName' sent to 'MailTo' Distribution List, both described in init
#
############################################################################################


def SendEmail():
    print "Sending mail"
    Header = "\"NetBackup daily log for " + Hostname + "\""       # Title of the mail
    cmd="mail -s " + Header + " " + MailTo + " < " + ReportFileName     # Insert bp command to run here
    print cmd
    Output,Error=subprocess.Popen (cmd,shell=True, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()       # Sends cmd to the subprocess
                                                                        # Shell=True waits for the response and allows direct output.


############################################################################################
#
#  Main
#
############################################################################################

ReportFileName = HostFolder + report_file_name()
print "File Output folder and name", ReportFileName
gather_jobs(ReportFileName)
print "Output file created"


### End nbdailylog.py ###
