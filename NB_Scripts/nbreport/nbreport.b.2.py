#!/usr/bin/python
# nbreport.py
Version = 'b.2'
#
# Author: Terry Carter/Roberto Garcia
#
# v b.2 added tape backup checks.
# v b.1 added Prakash and Pushpinder to email. Revised error code section
#
# This script:
#       Gets a list of all assigned clients
#       A) Reports if any clients do not have backups for the past two days
#       B) Read in a list of clients from active directory (report provided)
#               Reports on any hosts in AD that are NOT a client
#               Reports on any hosts that are clients that are not in AD
#
# Future Update requests
# 1) Report on the status of the last backup (status 0, status 1 or other)
# 2) For status 1, what files were missed
# 3) Log time of backup - POM reporting
# 4) Report on volume of space used on disk storage
#
############################################## Init ##############################################
# Here are all of the things needed to initialize the processes used.
############################################################################################

# Local imports #
from column import indent                               # Local script that prints in columns
from nbjobs import parse_jobs                           # Lists long running jobs
from nblibdir import library_status                     # Lists library status
from nblibdir import drive_status                       # Lists drive status

# Global imports #
import re                                               # Used to replace items
import shlex                                            # used to format lines for Popen
import subprocess                                       # Used for Popen, directions to the command line
import datetime                                         # Used for date and relative date information

#import smtplib                                         # Import smtplib for the actual sending function
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText

import socket                                           # Used to get host information
Hostname = socket.gethostname()                         # Get host name
FQDN = socket.getfqdn()                                 # Get fully qualified host name
#print Hostname
#print FQDN

#MailTo = """cit_backups_us_grp@oracle.com, sanair_org_ww@oracle.com, om.nigam@oracle.com, prakash.trivedi@oracle.com, pushpinder.pandher@oracle.com"""  # List the people to mail to
#MailTo = "cit_backups_ww_grp@oracle.com"
MailTo = """terry.carter@oracle.com, roberto.b.garcia@oracle.com"""  # List the people to mail to
ReportFileName = "/tmp/nbreportfile.tmp"                # Location of report file used for mailing


############################################## ListClients ##############################################
# This gets a list of all of the clients assigned in NetBackukp
############################################################################################


def ListClients():
    print "Getting a list of clients"
    OutputArray = []                                      # Clears the output array
    TotalClients = 0
# cmd ="/usr/openv/netbackup/bin/admincmd/bperror -U -backstat -by_statcode -hoursago ${HOURS} >> ${TEMP}"
    cmd="/usr/openv/netbackup/bin/admincmd/bpplclients"   # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                               # Formats the string to be used with Popen - splits on spaces
    output,error=subprocess.Popen (args,stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

    output = re.sub(' +',' ',output)                      # Takes multiple spaces and converts to one space
    output = output.splitlines()                          # Splits multiple line var into one line per array element

    for line in output:                                   # For each line in the array
        line = line.split()                                 # Split each item on each line
        OutputArray.append(line [2])                        # Save this to an array
        TotalClients = TotalClients + 1                     # Add up Total Clients
    return OutputArray, TotalClients


############################################## LastBackup ##############################################
# For all of the host names in List, we look up the latest and latest full backups.
# If the latest backup is more than 2 days ago, we throw an error
# If the latest full backup is more than a week ago (Roughly 192 hours), we throw an error
# If the request for backups throws an error, we pass it on
############################################################################################


def LastBackup(List):
    print "Checking clients for backups"
    Today = datetime.date.today()                         # Get today's date
    TwoDaysAgo = Today - datetime.timedelta(days=2)       # Get the date for 2 days ago

    FullOutArray = [['Host','Last Backup','Full Backup','Status']]        # Create headers for arrays
    ErrorOutArray = [['Host','Last Backup','Full Backup','Status']]
    NumErrorClients = 0                                   # Zero the number of clients with errors counter

                ### Loop through all hosts ###
    for x in range(2,len(List)):                          # Skip the first two header lines. Cycle through the rest of the array
        HostErrorFlag = False
        # cmd="/usr/openv/netbackup/bin/admincmd/bperror -U -backstat -by_statcode -hoursago ${HOURS} >> ${TEMP}"
        cmd="/usr/openv/netbackup/bin/admincmd/bpimagelist -U -client " + List[x] + " -hoursago 192" # Insert bp command to run here
#        print cmd
        args = shlex.split(cmd)                             # Formats the string to be used with Popen - splits on spaces
        Output,Error=subprocess.Popen (args,stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

        if Error == "":                                     # No error from the Popen command
            Output = Output.splitlines()                      # Splits multiple line var into one line per array element
            OutputArray = []                                  # Clears the output array
            for Line in Output:                               # For each line in the array
                Line = Line.split()                             # Split each item on each line
                OutputArray.append(Line)                        # Save this to an array

            LastBackupDate = OutputArray [2][0]               # Capture the last valid backup date
            FormattedLastBackupDate = datetime.datetime.strptime(LastBackupDate, "%m/%d/%Y")  # Convert last backup date into a date variable

                ### Was the latest backup more than two days ago? ###
            if FormattedLastBackupDate.date() < TwoDaysAgo:   # Was the last backup more than 2 days ago?
                HostStatus = "Last backup too old, "
                HostErrorFlag = True                            # Flag there was a backup error with this host
            else:                                             # Backup is fine
                HostStatus = "Last backup is fine, "

            ValidFullBackup = False                           # Capture the last full backup date

                ### Loop through all of the backups for the host to look for Full backup ###
            for y in range(len(OutputArray)):                 # Loop through all the lines in the output
                if OutputArray[y][6] == "Full":                 # Check to see if it's a full backup
                    ValidFullBackup = True                        # Set flag that it's a full backup
                    ValidFullBackupDate = OutputArray[y][0]       # Get the date of the full backup

            if ValidFullBackup == True:                       # Print info on full backup condition
                HostStatus = HostStatus + "Full backup is fine"
            else:                                             # No Full backups in the last week
                HostStatus = HostStatus + "Missing Full backup"
                HostErrorFlag = True                            # Flag there was a backup error with this host
                ValidFullBackupDate = '00/00/0000'
            FullOutArray.append([List[x],LastBackupDate,ValidFullBackupDate,HostStatus])      # Append the status to the array

        else:                                               # We got an error from the Popen command
            Error = re.sub('\r','',Error)                     # take out carriage returns
            Error = re.sub('\n','',Error)                     # take out Line feeds
            HostErrorFlag = True                              # Flag there was a backup error with this host
            LastBackupDate = '00/00/0000'
            ValidFullBackupDate = '00/00/0000'
            HostStatus = Error
            FullOutArray.append([List[x],LastBackupDate,ValidFullBackupDate,HostStatus])      # Append the status to the array

                ### If there was an error on the Full or last backup, log it in the error list and count ###
        if HostErrorFlag:
#      ErrorOutArray.append([List[x],'00/00/0000','00/00/0000',Error])
            ErrorOutArray.append([List[x],LastBackupDate,ValidFullBackupDate,HostStatus])      # Append the status to the array
            NumErrorClients = NumErrorClients + 1             # Increment number of clients with errors count

    return FullOutArray, ErrorOutArray, NumErrorClients   # Return full results, error results and number of clients with errors.


############################################## GetStsCode ##############################################
# List error clients results with status code
############################################################################################


def GetStsCode(ErrorOutArray):
    ErrCodeReport_array = []                              # initialize array
    print "Getting a list of clients with errors"
    ErrCodeReport = "\n"                                  # Initializing error code report variable

    for line in range(1,len(ErrorOutArray)):              # Loop through all of the hosts reporting a failure
        hostname = ErrorOutArray[line][0]                   # Get the host name
                                                        # Get the status of the failed host over the last 24 hours
        cmd ="/usr/openv/netbackup/bin/admincmd/bperror -client " + hostname + " -backstat"
        args = shlex.split(cmd)                             # Formats the string to be used with Popen - splits on spaces
        Output,Error=subprocess.Popen (args,stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

        if Output:                                          # Only sort when we get output, not errors
            Output_words = Output.split()                     # Split the output into words
            host_error = Output_words[len(Output_words)-1]    # The error nubmer is from the last backup, last item in the string
            ErrCodeReport_array.append([int(host_error),hostname])    # write error number and host to an array

    ErrCodeReport_array.sort()                            # Sort the array after it's completely written

    ErrCodeReport = "\n"                                  # Initializing error code report variable
    last_error = 400                                      # init the last_error to something that will be new on first test
    for line in range(len(ErrCodeReport_array)):          # Sift through all the lines of the array and format for test
        if last_error <> ErrCodeReport_array[line][0]:      # Is this the same error we had last time
            last_error = ErrCodeReport_array[line][0]         # Update the last error code we got
            ErrCodeReport += "\n"                             # Add newline for each error code

            cmd ="/usr/openv/netbackup/bin/admincmd/bperror -statuscode " + str(last_error)
            args = shlex.split(cmd)                           # Formats the string to be used with Popen - splits on spaces
            Output,Error=subprocess.Popen (args,stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
            if Output:                                        # If we get a description of the error code...
                ErrCodeReport += str(last_error) + " " + Output.splitlines()[0] + "\n"  # save the number AND the short error description
            else:                                             # Otherwise
                ErrCodeReport += str(last_error) + "\n"         # Just print the error number
        ErrCodeReport += str(ErrCodeReport_array[line][1]) + "\n"   # Add the host beneath the error code/desc heading

    return ErrCodeReport                                  # Return the formatted output


########################################################################
# Get_Policies
# Return a list of Policies
########################################################################


def get_policies():
    cmd = "/usr/openv/netbackup/bin/admincmd/bppllist"  # Insert whatever bp command you want to run here
    args = shlex.split(cmd)  # Formats the string to be used with Popen - splits on spaces
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error
    else:
        return output


########################################################################
# Check_Policy_Library
# Checks to see if there is a vault policy which means there is a library attached
# Returns if found (True) or not (False)
########################################################################


def check_policy_library():
    output = get_policies()
    output = output.splitlines()    # Splits multiple line var into one line per array element
    for line in output:             # For each line in the array
        if "Vault" in line:     # the word "Vault" means we have a library attached
            print line + " has the word Vault in it"
            return True                # Policy name found
    return False                # Policy name not found


############################################## LastTapeBackup ##############################################
# For all of the host names in List, we look up the latest and latest full backups.
# If the latest backup is more than 2 days ago, we throw an error
# If the latest full backup is more than a week ago (Roughly 192 hours), we throw an error
# If the request for backups throws an error, we pass it on
############################################################################################


def LastTapeBackup(List):
    print "Checking clients for tape backups"
    Today = datetime.date.today()                         # Get today's date
    TwoDaysAgo = Today - datetime.timedelta(days=2)       # Get the date for 2 days ago

    FullOutArray = [['Host','Last Backup','Full Backup','Status']]        # Create headers for arrays
    ErrorOutArray = [['Host','Last Backup','Full Backup','Status']]
    NumErrorClients = 0                                   # Zero the number of clients with errors counter

                ### Loop through all hosts ###
    for x in range(2,len(List)):                          # Skip the first two header lines. Cycle through the rest of the array
        HostErrorFlag = False
        # cmd="/usr/openv/netbackup/bin/admincmd/bperror -U -backstat -by_statcode -hoursago ${HOURS} >> ${TEMP}"
        cmd="/usr/openv/netbackup/bin/admincmd/bpimagelist -U -client " + List[x] + " -hoursago 192 -tape" # Insert bp command to run here
#        print cmd                                      ### For Troubleshooting
        args = shlex.split(cmd)                             # Formats the string to be used with Popen - splits on spaces
        Output,Error=subprocess.Popen (args,stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

        if Error == "":                                     # No error from the Popen command
#            print Output                                       ### For Troubleshooting
            Output = Output.splitlines()                      # Splits multiple line var into one line per array element
            OutputArray = []                                  # Clears the output array
            for Line in Output:                               # For each line in the array
                Line = Line.split()                             # Split each item on each line
                OutputArray.append(Line)                        # Save this to an array

            LastBackupDate = OutputArray [2][0]               # Capture the last valid backup date
            FormattedLastBackupDate = datetime.datetime.strptime(LastBackupDate, "%m/%d/%Y")  # Convert last backup date into a date variable

                ### Was the latest backup more than two days ago? ###
            if FormattedLastBackupDate.date() < TwoDaysAgo:   # Was the last backup more than 2 days ago?
                HostStatus = "Last backup too old, "
                HostErrorFlag = True                            # Flag there was a backup error with this host
            else:                                             # Backup is fine
                HostStatus = "Last backup is fine, "

            ValidFullBackup = False                           # Capture the last full backup date

                ### Loop through all of the backups for the host to look for Full backup ###
            for y in range(len(OutputArray)):                 # Loop through all the lines in the output
                if OutputArray[y][6] == "Full":                 # Check to see if it's a full backup
                    ValidFullBackup = True                        # Set flag that it's a full backup
                    ValidFullBackupDate = OutputArray[y][0]       # Get the date of the full backup

            if ValidFullBackup == True:                       # Print info on full backup condition
                HostStatus = HostStatus + "Full backup is fine"
            else:                                             # No Full backups in the last week
                HostStatus = HostStatus + "Missing Full backup"
                HostErrorFlag = True                            # Flag there was a backup error with this host
                ValidFullBackupDate = '00/00/0000'
            FullOutArray.append([List[x],LastBackupDate,ValidFullBackupDate,HostStatus])      # Append the status to the array
        else:                                               # We got an error from the Popen command
            Error = re.sub('\r','',Error)                     # take out carriage returns
            Error = re.sub('\n','',Error)                     # take out Line feeds
            HostErrorFlag = True                              # Flag there was a backup error with this host
            LastBackupDate = '00/00/0000'
            ValidFullBackupDate = '00/00/0000'
            HostStatus = Error
            FullOutArray.append([List[x],LastBackupDate,ValidFullBackupDate,HostStatus])      # Append the status to the array

                ### If there was an error on the Full or last backup, log it in the error list and count ###
        if HostErrorFlag:
#      ErrorOutArray.append([List[x],'00/00/0000','00/00/0000',Error])
            ErrorOutArray.append([List[x],LastBackupDate,ValidFullBackupDate,HostStatus])      # Append the status to the array
            NumErrorClients = NumErrorClients + 1             # Increment number of clients with errors count

    return FullOutArray, ErrorOutArray, NumErrorClients   # Return full results, error results and number of clients with errors.


############################################## get_jobs ##############################################
# Retrieve long running jobs
# Format for nice printing
############################################################################################


def get_jobs(job_time):
    long_jobs = parse_jobs(job_time)                                      # find long running jobs
    job_return = "Active Backup Jobs\n"
    if long_jobs == []:
        job_return += "All jobs running on time"
    else:
        for line in long_jobs:                          # Read through all the lines
            job_return += " ".join(("Host", line[0] , "/ Backup job", line[1], " has been running for over", str(line[2]), "Hours\n"))

    return job_return

############################################## MakeEmail ##############################################
# Open a file and create the body of the email to send
############################################################################################


def MakeEmail(Total, Full, Error, NumError, StsCode, FullTape, ErrorTape, NumErrorTape, has_library, job_status):
    print "Creating file to mail"
    SuccessHost = Total - NumError
    SuccessRate = int(float(SuccessHost) / Total  * 100)
    FailureRate = 100 - SuccessRate
    SuccessHostTape = Total - NumErrorTape
    SuccessRateTape = int(float(SuccessHostTape) / Total  * 100)
    SuccessRateTapeJob = 100 - (SuccessRate - SuccessRateTape)

    with open(ReportFileName,'w') as ReportFile:
# Header
        ReportFile.write("Netbackup report for " + Hostname + "\n")
        if has_library:
            ReportFile.write("with attached tape library\n")
        ReportFile.write("\n")

# Host Count
        ReportFile.write("Total Configured host - " + str(Total) + "\n")    # Print overall statistic

# Library status
        if has_library:
            ReportFile.write("\n")
            ReportFile.write("Library Status\n")
            status = library_status()
            for line in status:
                ReportFile.write(line[0])
                ReportFile.write("\n")

# Tape drive status
            ReportFile.write("\n")
            ReportFile.write("Tape Drive Status\n")
            status = drive_status()
            labels = ('Drive Name', 'Server', 'Dr#', 'Device', 'Status')
            ReportFile.write(indent([labels]+status, hasHeader=True))

# Job status - long running jobs
        ReportFile.write("\n")
        ReportFile.write(job_status)

# Disk backup overview
        ReportFile.write("\n")
        ReportFile.write("Disk Backups\n")
        ReportFile.write("Successful backed up hosts to disk- " + str(SuccessHost) + "\n")
        ReportFile.write("Failed hosts - " + str(NumError) + "\n")
        ReportFile.write("Host protection rate - " + str(SuccessRate) + "%\n")
        ReportFile.write("Host at risk - " + str(FailureRate) + "%\n")

# Tape backup overview
        if has_library:
            ReportFile.write("\n")
            ReportFile.write("Tape Backups\n")
            ReportFile.write("Successful backed up hosts to tape- " + str(SuccessHostTape) + "\n")
            ReportFile.write("Failed hosts - " + str(NumErrorTape) + "\n")
            ReportFile.write("Tape Protection Rate - " + str(SuccessRateTape) + "%\n")
            ReportFile.write("Tape Job Success Rate - " + str(SuccessRateTapeJob) + "%\n")

# Disk backup failure
        ReportFile.write("\n")                              # Print failed host
        ReportFile.write("***** Disk Backup Failures *****\n")
        ReportFile.write(indent(Error, hasHeader=True))

# Disk backup failure sorted by code
        ReportFile.write("\n")                              # Print status code section
        ReportFile.write("*****Disk Failure Status Code*****")
        ReportFile.write(StsCode + "\n")

# Tape backup failures
        if has_library:
            ReportFile.write("\n")                              # Print failed host
            ReportFile.write("***** Tape Backup Failures *****\n")
            ReportFile.write(indent(ErrorTape, hasHeader=True))

# Disk backup logs
        ReportFile.write("\n")                              # Print full logs
        ReportFile.write("***** Disk Backup Logs *****\n")
        ReportFile.write(indent(Full, hasHeader=True))

# Tape backup logs
        if has_library:
            ReportFile.write("\n")                              # Print full logs
            ReportFile.write("***** Tape Backup Logs *****\n")
            ReportFile.write(indent(FullTape, hasHeader=True))

# Version information
        ReportFile.write("\n")                              # Print version number
        ReportFile.write(Version + "\n")


############################################## SendEmail ##############################################
# Send a mail the the recipients with the previously formatted body
############################################################################################


def SendEmail():
    print "Sending mail"
    Header = "\"Windows NetBackup results for " + Hostname + "\""         # Title of the mail
    cmd="mail -s " + Header + " " + MailTo + " < " + ReportFileName       # Insert bp command to run here
    print cmd
#  args = shlex.split(cmd)                                              # Formats the string to be used with Popen - splits on spaces
#  print args
#  Output,Error=subprocess.Popen (args,stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
    Output,Error=subprocess.Popen (cmd,shell=True, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()       # Sends cmd to the subprocess
                                                                        # Shell=True waits for the response and allows direct output.

                                                                        # Example of sendmail vs mail. Allows for fixed width fonts
""" [root@epdc01nbadm01 ~]# (
> echo "From: tscarter@epdc01nbadm01";
> echo "To: terry.carter@oracle.com";
> echo "Subject: Testing Sendmail"
> echo "Content-Type: text/html";
> echo "MIME-Version: 1.0";
> cat /tmp/nbreportfile.tmp
> ) | sendmail -t
"""


############################################## Main ##############################################

### Overall Data
ClientsInPolicy, TotalNumClients = ListClients()                                # Get a list and number of clients.
has_library = check_policy_library()

### Disk Data
FullOutArray, ErrorOutArray, NumErrorClients = LastBackup(ClientsInPolicy)      # Get two arrays of all backups and those that failed
StsCodeErr = GetStsCode(ErrorOutArray)                                          # Get a list of status code errors

### Tape Data
if has_library:
    print "This domain has a tape library"
    FullOutArrayTape, ErrorOutArrayTape, NumErrorClientsTape = LastTapeBackup(ClientsInPolicy)

### Get Job Information
job_status = get_jobs(24)
#print job_status

### Make it prety
MakeEmail(TotalNumClients, FullOutArray, ErrorOutArray, NumErrorClients, StsCodeErr, FullOutArrayTape, ErrorOutArrayTape, NumErrorClientsTape, has_library, job_status)      # Create file to email results
SendEmail()                                                                     # Format and send the mail
print "cat " + ReportFileName

#end
