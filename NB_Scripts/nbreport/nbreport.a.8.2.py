#!/usr/bin/python
# nbreport.py
Version = 'a.8.2'
#
# Author: Terry Carter
# V a.8.2 - PEP8 Compliant. Added sanair_org_ww@oracle.com
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
# ****************************** Init ******************************
# Here are all of the things needed to initialize the processes used.
# *******************************************************************

# Local imports #
from column import indent  # Local script that prints in columns

# Global imports #
import re  # Used to replace items
import shlex  # used to format lines for Popen
import subprocess  # Used for Popen, directions to the command line
import datetime  # Used for date and relative date information

# import smtplib                                         # Import smtplib for the actual sending function
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText

import socket  # Used to get host information

Hostname = socket.gethostname()  # Get host name
FQDN = socket.getfqdn()  # Get fully qualified host name
# print Hostname
# print FQDN

MailTo = """cit_backups_us_grp@oracle.com, sanair_org_ww@oracle.com, om.nigam@oracle.com"""  # List the people to mail to

# MailTo = """terry.carter@oracle.com, cit_backups_us_grp@oracle.com, sanair_org_ww@oracle.com,
#    om.nigam@oracle.com"""  # List the people to mail to

#MailTo = """terry.carter@oracle.com"""  # List the people to mail to Testing

ReportFileName = "/tmp/nbreportfile.tmp"  # Location of report file used for mailing


# ************************ list_clients ************************
# This gets a list of all of the clients assigned in NetBackukp
# **************************************************************
def list_clients():
    print "Getting a list of clients"
    output_array = []  # Clears the output array
    total_clients = 0
    cmd = "/usr/openv/netbackup/bin/admincmd/bpplclients"  # Insert whatever bp command you want to run here
    args = shlex.split(cmd)  # Formats the string to be used with Popen - splits on spaces
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    output = re.sub(' +', ' ', output)  # Takes multiple spaces and converts to one space
    output = output.splitlines()  # Splits multiple line var into one line per array element

    for line in output:  # For each line in the array
        line = line.split()  # Split each item on each line
        output_array.append(line[2])  # Save this to an array
        total_clients = total_clients + 1  # Add up Total Clients
    return output_array, total_clients


# ***************************************** last_backup *******************************************
# For all of the host names in List, we look up the latest and latest full backups.
# If the latest backup is more than 2 days ago, we throw an error
# If the latest full backup is more than a week ago (Roughly 192 hours), we throw an error
# If the request for backups throws an error, we pass it on
# ************************************************************************************************

def last_backup(client_list):
    print "Checking clients for backups"
    today = datetime.date.today()  # Get today's date
    two_days_ago = today - datetime.timedelta(days=2)  # Get the date for 2 days ago

    full_out_array = [['Host', 'Last Backup', 'Full Backup', 'Status']]  # Create headers for arrays
    error_out_array = [['Host', 'Last Backup', 'Full Backup', 'Status']]
    num_error_clients = 0  # Zero the number of clients with errors counter

#   *** Loop through all hosts ***
    for x in range(2, len(client_list)):  # Skip the first two header lines. Cycle through the rest of the array
        host_error_flag = False
        cmd = "/usr/openv/netbackup/bin/admincmd/bpimagelist -U -client " + client_list[
            x] + " -hoursago 192"  # Insert bp command to run here
        args = shlex.split(cmd)  # Formats the string to be used with Popen - splits on spaces
        output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        if error == "":  # No error from the Popen command
            output = output.splitlines()  # Splits multiple line var into one line per array element
            output_array = []  # Clears the output array
            for line in output:  # For each line in the array
                line = line.split()  # Split each item on each line
                output_array.append(line)  # Save this to an array

            last_backup_date = output_array[2][0]  # Capture the last valid backup date
            # Convert last backup date into a date variable
            formatted_last_backup_date = datetime.datetime.strptime(last_backup_date, "%m/%d/%Y")

            # *** Was the latest backup more than two days ago? ***
            if formatted_last_backup_date.date() < two_days_ago:  # Was the last backup more than 2 days ago?
                host_status = "Last backup too old, "
                host_error_flag = True  # Flag there was a backup error with this host
            else:  # Backup is fine
                host_status = "Last backup is fine, "

            valid_full_backup = False  # Capture the last full backup date

            # *** Loop through all of the backups for the host to look for Full backup ***
            for y in range(len(output_array)):  # Loop through all the lines in the output
                if output_array[y][6] == "Full":  # Check to see if it's a full backup
                    valid_full_backup = True  # Set flag that it's a full backup
                    valid_full_backup_date = output_array[y][0]  # Get the date of the full backup

            if valid_full_backup:            # Print info on full backup condition
                host_status = host_status + "Full backup is fine"
            else:                           # No Full backups in the last week
                host_status = host_status + "Missing Full backup"
                host_error_flag = True      # Flag there was a backup error with this host
                valid_full_backup_date = '00/00/0000'
            full_out_array.append(
                [client_list[x], last_backup_date, valid_full_backup_date, host_status])  # Append the status to the array

        else:  # We got an error from the Popen command
            error = re.sub('\r', '', error)  # take out carriage returns
            error = re.sub('\n', '', error)  # take out Line feeds
            host_error_flag = True  # Flag there was a backup error with this host
            last_backup_date = '00/00/0000'
            valid_full_backup_date = '00/00/0000'
            host_status = error
            full_out_array.append(
                [client_list[x], last_backup_date, valid_full_backup_date, host_status])  # Append the status to the array

            # *** If there was an error on the Full or last backup, log it in the error list and count ***
        if host_error_flag:
            #           error_out_array.append([List[x],'00/00/0000','00/00/0000',Error])
            error_out_array.append(
                [client_list[x], last_backup_date, valid_full_backup_date, host_status])  # Append the status to the array
            num_error_clients = num_error_clients + 1  # Increment number of clients with errors count

    return full_out_array, error_out_array, num_error_clients  # Full & error results & number of clients w/errors.


# ************************ MakeEmail ************************
# Open a file and create the body of the email to send
# ***********************************************************

def make_email(full, error, total, num_error):
    print "Creating file to mail"
    success_host = total - num_error
    success_rate = int(float(success_host) / total * 100)

    with open(ReportFileName, 'w') as ReportFile:
        ReportFile.write("Netbackup report for " + Hostname + "\n")
        ReportFile.write("\n")

        ReportFile.write("Total Configured host - " + str(total) + "\n")
        ReportFile.write("Successful backed up hosts - " + str(success_host) + "\n")
        ReportFile.write("Failed hosts - " + str(num_error) + "\n")
        ReportFile.write("Success Rate - " + str(success_rate) + "%\n")

        ReportFile.write("\n")
        ReportFile.write("***** Failures *****\n")
        ReportFile.write(indent(error, hasHeader=True))
        ReportFile.write("\n")
        ReportFile.write("***** Logs *****\n")
        ReportFile.write(indent(full, hasHeader=True))
        ReportFile.write("\n")
        ReportFile.write(Version + "\n")


# **************************** SendEmail ****************************
# Send a mail the the recipients with the previously formatted body
# *******************************************************************


def send_email():
    print "Sending mail"
    header = "\"Windows NetBackup results for " + Hostname + "\""  # Title of the mail
    cmd = "mail -s " + header + " " + MailTo + " < " + ReportFileName  # Insert bp command to run here
    print cmd
    #   args = shlex.split(cmd)                           # Formats the string to be used with Popen - splits on spaces
    #   print args
    #   output,error=subprocess.Popen (args,stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
    output, error = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE).communicate()  # Sends cmd to the subprocess
    # Shell=True waits for the response and allows direct output.


"""# Example of sendmail vs mail. Allows for fixed width fonts

   [root@epdc01nbadm01 ~]# (
> echo "From: tscarter@epdc01nbadm01";
> echo "To: terry.carter@oracle.com";
> echo "Subject: Testing Sendmail"
> echo "Content-Type: text/html";
> echo "MIME-Version: 1.0";
> cat /tmp/nbreportfile.tmp
> ) | sendmail -t
"""

# ************************ Main ************************
clients_in_policy, total_num_clients = list_clients()  # Get a list and number of clients.
full_out_array, error_out_array, num_error_clients = last_backup(
    clients_in_policy)  # Get two arrays of all backups and those that failed
make_email(full_out_array, error_out_array, total_num_clients, num_error_clients)  # Create file to email results
send_email()  # Format and send the mail
print "cat " + ReportFileName
# end
