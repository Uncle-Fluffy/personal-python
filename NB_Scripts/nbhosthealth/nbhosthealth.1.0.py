#!/usr/bin/python
#
# nbhosthealth.py
#
# This script looks at the length of jobs running in the NBU environment
#
#
# Created: Terry Carter
# Date: 1/23/2019
#
#
# Future featur update requests
# 1) Grab the NBU version from the NBU Admin and compare to all hosts. All hosts should be up to the admin level
# 2) Decide and comment properly if we have NO connections or rev problems
#

version = "1.0"


########################################################################
#   Init / Include
########################################################################


# Local imports #
from column import indent                               # Local script that prints in columns

import subprocess                                       # Used for Popen, directions to the command line
import shlex                                            # used to format lines for Popen

import socket                                           # Used to get host information
Hostname = socket.gethostname()                         # Get host name

MailTo = "cit_backups_ww_grp@oracle.com"                # List the people to mail to
#MailTo = "terry.carter@oracle.com"                     # List the people to mail to

ReportFileName = "/tmp/nbhostreportfile.tmp"            # Location of report file used for logging
mailto_filename = "/tmp/mailbody.tmp"                   # File used for the body of the mail

########################################################################
#
#   Get_Hosts_from_NBU
# Requests a list of hosts names from NBU
# Parses the result for just the host names
# Returns a simple list of host names
#
########################################################################


def get_hosts_from_nbu():
    cmd = "/usr/openv/netbackup/bin/admincmd/bpplclients"
    args = shlex.split(cmd)                     # Shlex allows to read the spaces on the cmd line.
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error
    output = output.split('\n', 2)[2]           # Trim the first two lines off the output

    nbu_hosts = ""                              # Initialize to string type
    for line in output.splitlines():            # Split the out put into strings
        fields = line.split()                   # Split each line into fields
        nbu_hosts += fields[2] + '\n'           # assemble just the 3rd colum

    return nbu_hosts                            # Return a simple text list of host names


########################################################################
#
#    get_host_status
#  Gets the status of each host
#
########################################################################


def get_host_status():
    print "Getting host status(s)"
    try:
        server_list = get_hosts_from_nbu()                      # Get a list of hosts
    except ValueError as error:
        raise ValueError(error)                                 # Stop work, Pass the error up to the next level

    with open(ReportFileName,'w+') as ReportFile:               # Open a report file

        for server in server_list.splitlines():                 # Split the list into individual names
            cmd = "/usr/openv/netbackup/bin/admincmd/bpgetconfig -l -g " + server # Insert whatever bp command you want to run here
            args = shlex.split(cmd)                                 # Formats the string to be used with Popen - splits o
            output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

            if error:                                           # Host having communications problem
                error = error.splitlines()[0]                   # Grab just the first line
                print server, "Failed:", error                  # only print the first line
                ReportFile.write(server + " Failed: " + error + "\n")   # Write the result to a file

            else:                                               # Good results from host status request
                print server, output,                           # Used for debugging and watching script progress status

                if "Linux" in output:                           # lixux servers look different
# Master;Linux, RedHat2.6.18;8.1.0;NetBackup;8.1.1;810000;/usr/openv/netbackup/bin;Linux 4.1.12-112.14.13.el6uek.x86_64 ;
                    host_and_processor = output.split()[2]      # Split out the host and processor type
                    if "64" in host_and_processor.split(".")[-1]:       # look for 64 bit
                        processor_bits = "64-Bit"               # Print common output for 64 bit types
                    else:
                        processor_bits = "32-Bit"               # else print 32 bit
                    os = output.split(";")[1].split()[1]        # Parse out OS type
                    nbu_ver = output.split(";")[4]              # Parse out NBU version

                else:                                           # Windows box
# Client of adc08nbuadm01-nfs.us.oracle.com;PC-x64, WindowsXP;8.1.0;NetBackup;8.1.1;810000;C:\Program Files\VERITAS\NetBackup\bin;Windows2008 6 ;
                    host_and_processor = output.split()[2]      # Split out the host and processor type
                    if "64" in host_and_processor.split(";")[1]: # look for 64 bit
                        processor_bits = "64-Bit"               # Print common output for 64 bit types
                    else:
                        processor_bits = "32-Bit"               # else print 32 bit
                    os = output.split(";")[7].split()[0]        # Parse out OS type
                    nbu_ver = output.split(";")[4]              # Parse out NBU version

                print server, nbu_ver, os, processor_bits       # Print just the status info we need
                ReportFile.write(server + " " + nbu_ver + " " + os + " " + processor_bits + "\n")       # Save the status to a file

    print "To read file, cat", ReportFileName                   # Just a help comment if running directly


########################################################################
#
#    filter_host_status
#  Sift through all of the status returns of the different host
#  Filter out:
#  1) Hosts that are having a problem connecting to the admin box
#  2) Hosts that could be upgraded/have an old version of NBU
#
########################################################################


def filter_host_status(nbu_ver):                                # Pass latest NBU version in

    failed_host_array = [['Host','Message']]                    # Set headers for both arrays
    downrev_host_array = [['Host','NBU Ver','OS/Version','HW Bit']]

    with open(ReportFileName,'r') as ReportFile:                # Open the report file for reading
        for line in ReportFile:                                 # Read through all the lines in the report

            if "Failed" in line:                                # if we have failed communication
                host = line.split (' ', 1)[0]                   # Grab the host name, first item before the first space
                error = line.split (' ', 1)[1].strip('\n')      # Rest of the line after the first space, strip the \n
                failed_host_array.append([host,error])          # append to the failed host array

            elif ("64-Bit" in line) and (nbu_ver not in line):  # 64 bit and not up to latest rev
                downrev_host_array.append(line.split())         # Split each item into down rev array

    return failed_host_array, downrev_host_array                # Return the two arrays


########################################################################
#
#   format_mail
# Format a file to send out as the body of a mail
#
########################################################################


def format_mail(failed,downrev):                                # Receive the two arrays
    with open(mailto_filename,'w+') as formatfile:              # Open a file to write the formatted email

        formatfile.write("*** The NBU admin can not connect to the following host(s) ***\n") # Write header
        formatfile.write(indent(failed, hasHeader=True))        # Format and write contents
        formatfile.write("\n")

        formatfile.write("*** The following require NBU update ***\n") # Write header for updates
        formatfile.write(indent(downrev, hasHeader=True))       # Format and write contents


############################################## SendEmail ##############################################
# Send a mail the the recipients with the previously formatted body
############################################################################################


def SendEmail():
    print "Sending mail"
    Header = "\"NetBackup Host Health Status results for " + Hostname + "\""    # Title of the mail
    cmd="mail -s " + Header + " " + MailTo + " < " + mailto_filename            # Insert bp command to run here
    print cmd                                                                   # Helps if we need to resend or to verify receipients
    Output,Error=subprocess.Popen (cmd,shell=True, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()       # Sends cmd to the subprocess


########################################################################
#   __Main__
# Run only if local, not if called.
########################################################################


if __name__ == '__main__':                              # Execute only if ran locally
    get_host_status()                                   # Get the status's from each host.
    failed, downrev = filter_host_status("8.1.1")       # Filter hosts lower than given rev
    format_mail(failed,downrev)                         # Format for emailing
    SendEmail()                                         # Email list
