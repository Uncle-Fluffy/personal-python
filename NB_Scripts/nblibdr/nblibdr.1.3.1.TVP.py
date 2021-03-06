#!/usr/bin/python
#
# nblibdr.py
#
# This script feeds back many peices of information about attached tape libraries including
# checking the health and status of the library and drives on a NBU environment
# and tape information like scratch, recall and open slots.
#
#
# Created: Terry Carter
# Date: 1/16/2019
#
version = "1.3.1"

# Version information
# v 1.0 Origional
# v 1.1 TVP has robot attached to adm box not med. Had to fix that connection
# v 1.2 2/7/2019 Added tape information like scratch, recall and emtpy
#       Also added library name information
#       Fixed drive status eliminating pending requests v 1.3 4/11/2019 Fixed errors where even if the robot won't inventory, it
#       will report instead of crash
# v 1.3 12/2/2019 Fixed issue where inventory was failing.
#       Put in error handling
# v 1.3.1 12/9/2019 Added error handling to report on non reponsive Robot

########################################################################
#   Init / Include
########################################################################


import subprocess                                       # Used for Popen, directions to the command line
import shlex                                            # used to format lines for Popen

import socket                                           # Used to get host information

robot_matrix = [['adc08nbumed01.us.oracle.com','0','SL3K11'],
                ['adc08nbumed02.us.oracle.com','1','SL3k12'],
                ['llg07nbmedia01','0','LLG07SL3K02'],
                ['rmdc02nbumed01','0','RMDC-SL3K02'],
                ['sldc05nbumed01','0','SDC-SL3K03'],
                ['tvp02nbadm01.tvp.oracle.com','0','TVP-SL3k-01']]


########################################################################
#
#   get_media_servers
#  Gets a list of media servers
#
# Input: None
#  Calls: subprocess.Popen
# Output: string list of media server names with returns between
#
# Eg: adc08nbumed04
# adc08nbumed02
# adc08nbumed03
# adc08nbumed01
#
########################################################################


def get_media_servers():
#    print "Getting media servers"
    cmd = "/usr/openv/netbackup/bin/admincmd/bpgetconfig" # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                               # Formats the string to be used with Popen - splits o
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error

    return_servers = ""

    for line in output.splitlines():                    # grep out lines with "med" in them
        if "med" in line:
            return_servers += line.split()[2] + "\n"    # Same as awk '{print $3}'

    if return_servers == "":
        for line in output.splitlines():                    # grep out lines with "med" in them
            if "adm" in line:
                return_servers += line.split()[2] + "\n"    # Same as awk '{print $3}'

# This line is prety cool. It does something similar to a uniq in bash
# 'splitlines()' breaks up the string at the \n
# 'set' provides a uniq set of results
# We could use 'sorted' to sort after that
# 'join' adds them all back together with the item to it's left, a newline

    return_servers = '\n'.join(set(return_servers.splitlines())) # Remove duplicate servers

    return return_servers                               # Return a list of servers


########################################################################
#
#   drive_status
# show status of drives
#
# Drive status can be show by /usr/openv/volmgr/bin/vmoprcmd or
# by /usr/openv/volmgr/bin/tpconfig
#
# Input: None
#  Calls: get_media_servers, subprocess.Popen
# Output: Array showing the status of all of the drives
#         Drive name, Media Server, Drive Number, Device attach point, Status
# Eg:
""" [['adc-sl3k11_0_10_17', 'adc08nbumed01', '1', '/dev/nst3', 'UP'], ['adc-sl3k11_0_10_18', 'adc08nbumed01', '0', '/dev/nst0', 'UP'], ['adc-sl3k11_0_10_19', 'adc08nbumed02', '3', '/dev/nst0', 'UP']] """
#
########################################################################


def drive_status():
    dev_dict = {}
    dev_array = []

    try:
        server_list = get_media_servers()                       # Get a list of media servers
    except ValueError as error:
        raise ValueError(error)                                 # Stop work, Pass the error up to the next level

# Drive Status
    for server in server_list.splitlines():
        cmd = "/usr/openv/volmgr/bin/vmoprcmd -dp ds -h " + server # Insert whatever bp command you want to run here
        args = shlex.split(cmd)                                 # Formats the string to be used with Popen - splits o
        output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if error:
            raise ValueError(error)                             # Pass the Popen error

        for lines in output.splitlines():                       # list through output
            if lines != "":                                     # Ignore blank lines
                if lines.split()[0].isdigit():                  # 1st item on the line is a digit
                    dev_dict.update({server  + " " + lines.split()[0] : lines.split()[1] + " " + lines.split()[2]})

# Additional Drive Status
    for server in server_list.splitlines():
        cmd = "/usr/openv/volmgr/bin/vmoprcmd -dp ad -h " + server # Insert whatever bp command you want to run here
        args = shlex.split(cmd)                                 # Formats the string to be used with Popen - splits o
        output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if error:
            raise ValueError(error)                             # Pass the Popen error

        for lines in output.splitlines():                       # list through output
            if lines != "":                                     # Ignore blank lines
                if lines.split()[0].isdigit():                  # 1st item on the line is a digit
                    dev_array.append([lines.split()[1],
                                      server,
                                      lines.split()[0],
                                      dev_dict.get(server  + " " + lines.split()[0]).split()[0],
                                      dev_dict.get(server  + " " + lines.split()[0]).split()[1]
                                      ])                    # format array output


#    print sorted(dev_array, key=lambda item: item[0])          # Another form of sort. Keep for reference
    dev_array.sort(key=lambda item: item[0])                    # Sort by drive name
    return dev_array


########################################################################
#
#  get_robot_connections
# Gets connections where tape library robots are attached to media servers
#
# Input: None
#  Calls: subprocess.Popen
# Output: Returns an array of TLD#, Admin server, Media Server, Connection
#
# Eg:
""" [['0', 'adc08nbuadm01.us.oracle.com', 'adc08nbumed01.us.oracle.com', '/dev/sg7'], ['1', 'adc08nbuadm01.us.oracle.com', 'adc08nbumed02.us.oracle.com', '/dev/sg2']] """
#
########################################################################


def get_robot_connections():
    return_array = []
    cmd = "/usr/openv/volmgr/bin/tpconfig -emm_dev_list"        # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                                     # Formats the string to be used with Popen - splits o
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                                 # Pass the Popen error

# Find the total number(s) of robots that NBU thinks it has
    robot_number_array = []

    for lines in set(output.splitlines()):                      # Search through only unique lines
        if "Robot Number" in lines:                             # Find robot numbers
            robot_number_array.append([str(int(lines.split(":")[1]))])
#    robot_number_array.append(['99'])  # fakie robot number


# Find each robot and it's connection to the environment
    for line in output.splitlines():                            # Search through each line
        if "Robot Number" in line:                              # Found a robot
            robot_number = str(int(line.split(":")[1]))         # Grab 1st item after the :, turn it into an integer>str
            path_found = False                                  # New robot found

        elif "Media Server" in line:                            # Found Media Server
            media_server = line.split(":")[1].lstrip()                  # Grab 1st item after the :

        elif "Apath" in line:                                   # Found robot connection
            path = line.split(":")[1].lstrip()                  # Grab 1st item after the :
            if "-" not in path:
                path_found = True                               # This is a valid Robot connection

        elif "VMhost" in line:                                  # Found EMM server
            if path_found:                                      # First EMM found after robot connectivity. That's a group!
                emm_server = line.split(":")[1].lstrip()        # Grab 1st item after the :
                return_array.append([robot_number, emm_server, media_server, path])

#    return_array.append(['5', 'adc08nbuadm01.us.oracle.com', 'adc08nbumed01.us.oracle.com', '/dev/sg9']) # Fakie for a neg test

    for robot in robot_number_array:                            # Make sure all the NBU robots have connections
        robot_found = False                                     # Initialize flag
        for connection in return_array:                         # Loop through the connections that were found
            if robot[0] == connection[0]:                       # If we found a robot for each one NBU knew about
                robot_found = True                              # Mark we found one
        if not robot_found:                                     # If we looped through all but didn't find it
            return_array.append([robot[0], 'No', 'Connection', 'Found']) # Make a fake robot entry

    return return_array                                         # Return the result array


########################################################################
#
#  library_status
# show if library is up/down
# through inventory status, you can tell if the library is responding
#
# Input: None
#  Calls: get_robot_connections, subprocess.Popen
# Ouptut: Array showing the status of the library(s)
#
# Eg: [['Robot 0 is responding normally'], ['Robot 1 is responding normally']]
#
########################################################################

def library_status():
    status_array = []
    connections = get_robot_connections()

    for line in connections:
        if line[1] == "No":                                     # No valid robot found
            status_array.append(["Robot " + line[0] + " has no connectivity"])

        else:                                                   # Valid robot found
#             Example string: -rn 0 -rt TLD -h adc08nbuadm01.us.oracle.com -rh adc08nbumed02.us.oracle.com
            dash_string = "-rn " + line[0] + " -rt TLD -h " + line[1] + " -rh " + line[2]
            cmd = "/usr/openv/volmgr/bin/vmcheckxxx " + dash_string         # Insert whatever bp command you want to run here
            args = shlex.split(cmd)                             # Formats the string to be used with Popen - splits o
            output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

            if "Robot Contents" in output:                      # Received a valid inventory
                status_array.append(["Robot " + line[0] + " is responding normally"])
            else:                                               # Inventory did not respond correctly
                status_array.append(["Robot " + line[0] + " is not responding normally"])
                status_array.append(["    **** Please Fix Robot Connection Now **** "])

    return status_array                                         # Return findings


########################################################################
#
#  get_library_name
# Gets the name of the library
#
# Input: robot number, robot host
#  Calls: None
# Output: Text - Robot name
#
########################################################################


def get_library_name(robot_number, robot_host):
    library_name = "robot"                              # Default name if I can't find it
    for line in range(len(robot_matrix)):               # Search through the matrix
        if ((robot_matrix [line] [0] == robot_host) and
            (robot_matrix [line] [1] == robot_number)): # Find a match
            library_name = robot_matrix [line] [2]      # Change the default name if found

    return library_name


########################################################################
#
#  do_inventory
# Runs inventory on given libraries
#
# Example commands
#Inv_11=$(/usr/openv/volmgr/bin/vmupdate -rt TLD -rn 0 -rh adc08nbumed01 -use_barcode_rules)
#Inv_12=$(/usr/openv/volmgr/bin/vmupdate -rt TLD -rn 1 -rh adc08nbumed02 -use_barcode_rules)
#
# Input: Robot number, Robot Host (Eg: 0,adc08nbumed01)
#  Calls: subprocess.Popen
# Ouptut: None - Passive call only
#
########################################################################


def do_inventory(robot_number,robot_host):
    cmd = "/usr/openv/volmgr/bin/vmupdate -rt TLD -rn " + robot_number + " -rh " + robot_host + " -use_barcode_rules"        # Insert whatever bp command you want to run here
    print cmd
    args = shlex.split(cmd)                                     # Formats the string to be used with Popen - splits o
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    if error:
        raise ValueError(error)                                 # Pass the Popen error


########################################################################
#
#  list_scratch
# Lists the available scratch for a given domain
#
# Bash Example commands and Sample Output
#/usr/openv/netbackup/bin/goodies/available_media |grep -i available|grep -v NONE|awk '{print $1}'|wc -l
#AN1627  HCART3   TLD      0        2      -       -          -  AVAILABLE
#AN1628  HCART3   TLD      1        4      -       -          -  AVAILABLE
#
# Input: TLD library number
#  Calls: subprocess.Popen
# Output: Value - Number of scratch tapes in that TLD
#
########################################################################


def list_scratch (tld):
    cmd = "/usr/openv/netbackup/bin/goodies/available_media"     # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                                     # Formats the string to be used with Popen - splits o
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                                 # Pass the Popen error

    count = 0                                           # Initialze counter
    for line in output.splitlines():                    # loop through every line of the output
        items = line.split()                            # Split each line into items
        if len(items) == 9:                             # If there are 9 items in the line
            if (items[2] == "TLD" and
                items[3] == tld and
                items[8] == "AVAILABLE"): # Matches scratch for this library
                count += 1
    return count


########################################################################
#
#  free_slots
# Count the free slots in a library
#
# Bash Example Command and Example Output
#/usr/openv/volmgr/bin/vmcheckxxx -rt tld  -list -rn 0 -rh adc08nbumed01 |grep No|wc -l
#/usr/openv/volmgr/bin/vmcheckxxx -rt tld  -list -rn 1 -rh adc08nbumed02 |grep No|wc -l
#  67      No
#  68      No
#
# Input: Robot Number, Name of the robot host (eg: 0,adc08nbumed01)
#  Calls: subprocess.Popen
# Output: Value - Number of empty slots in that TLD
#
########################################################################


def free_slots (robot_number,robot_host):
    cmd = "/usr/openv/volmgr/bin/vmcheckxxx -rt TLD -list -rn " + robot_number + " -rh " + robot_host      # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                                     # Formats the string to be used with Popen - splits o
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                                 # Pass the Popen error

    count = 0                                           # Initialze counter
    for line in output.splitlines():                    # loop through every line of the output
        if "No" in line:                                # Found an empty slot
            count += 1                                  # Increment couter
    return count                                        # Return total empty slots


########################################################################
#
#  recallable_media
# Find the media available for recall
#
# Bash Example Command and Example Output
##/usr/openv/netbackup/bin/goodies/available_media |grep -i available|grep NONE|awk '{print $1}'|wc -l)
#AN1467
#AN1010
#
# Input: None
#  Calls: subprocess.Popen
# Output: array - list of media ID to recall
#
########################################################################


def recallable_media():
    cmd = "/usr/openv/netbackup/bin/goodies/available_media"    # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                                     # Formats the string to be used with Popen - splits o
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                                 # Pass the Popen error

    output_array=[]
    for line in output.splitlines():                            # loop through every line of the output
        if (("AVAILABLE" in line) and ("NONE" in line)):        # Search for available media no in the library
            output_array.append(line.split() [0])               # build array of recallable media

    return output_array


########################################################################
#
#  tape_usage
# Gets data used in tape usage report
#
# Input: None
#  Calls: subprocess.Popen, socket.gethostname, os, fnmatch, time
# Output: Hostname, majority_media, media_seen, scratch_media,
#         one_week_vault, six_week_average, media_in_use
#
########################################################################


def tape_usage():
# Domain
    Hostname = socket.gethostname()                             # Get host name

# All Available/seen media
    cmd = "/usr/openv/netbackup/bin/goodies/available_media"    # Get a list of all available media
    args = shlex.split(cmd)                                     # Formats the string to be used with Popen - splits o
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                                 # Pass the Popen error

# Majority Media
    majority_matrix = []                                        # Create empty matrix for tape labels
    for line in output.splitlines():                            # Search through lines of output
        if "HCART" in line:                                     # Only lines with HCART3 have media in them
            majority_matrix.append(line.split()[0][:2])         # Append first word .split()[0], first two characters of each word [:2] (media family letters)

    count = [(i,majority_matrix.count(i)) for i in set(majority_matrix)]        # build a uniq set and count how many times each media family is found
    count.sort(key=lambda item: item[1], reverse=True)          # Sort count, use the second item in the list, highest number first
    majority_media = count[0][0]                                # Majority media is the first entry of the first line

# Majority Media seen, scratch, and in use
    media_seen = 0                                              # Zero media seen register
    scratch_media = 0                                           # Zero scratch media register
    for line in output.splitlines():                            # Search through lines of output
        if(("HCART" in line) and
           (majority_media in line)):                           # Line contains media and media is part of the majority
            media_seen += 1                                     # Add to media in rotation count
            if "AVAILABLE" in line:                             # Media Scratch
                scratch_media += 1                              # Add to scratch media count

    media_in_use = media_seen - scratch_media                   # Media in use

# Vault count for one and six weeks average
    import os, fnmatch                                          # 'os' Used to walk through directories, 'fnmatch' to match file name
    import time                                                 # 'time' used to determine age of file dates, how long ago

    in_dir = '/usr/openv/netbackup/vault/sessions'              # What directory to start looking through logs
    pattern = 'eject.list'                                      # Name of the file in the sub-directories that have the vault logs
    file_list = []                                              # Create new array for file name list

    now = time.time()                                           # Find the current time
    week_ago = now - (7 * 86400)                                # What was the time a week ago
    six_weeks_ago = now - (42 * 86400)                          # What was the time 6 weeks ago

# Create a list of all files that may contain vaulted tapes
    for d_name, sd_name, f_list in os.walk(in_dir):             # Grab a list of files that are below the base directory
        for file_name in f_list:                                # Walk through each file name
            if fnmatch.fnmatch(file_name, pattern):             # Match search string
                file_list.append(os.path.join(d_name, file_name))       # Append the file to the list if it matches

    one_week_tapes =[]                                          # Array for tape IDs
    six_week_tapes =[]                                          # Array for tape IDs

    for file_name in file_list:
        file_time = os.stat(file_name)                          # Get the stats on the file
        c_time = file_time.st_ctime                             # Time of last file change
        if c_time > week_ago:                                   # Test for a week ago which is also less than 6 weeks ago
            with open(file_name,'r') as preview_list:
                for line in preview_list:
                    if majority_media in line:                  # Is there a line with the majority media listed?
                        one_week_tapes.append(line.split(majority_media)[1].split()[0])        # Get just the tape numbers

        elif c_time > six_weeks_ago:                            # Test for more than a week ago but less than 6 weeks ago
            with open(file_name,'r') as preview_list:
                for line in preview_list:
                    if majority_media in line:                  # Is there a line with the majority media listed?
                        six_week_tapes.append(line.split(majority_media)[1].split()[0])        # Get just the tape numbers

    one_week_vault = len(set(one_week_tapes))                   # How many uniqe tapes were vaulted last week?
    six_week_vault = one_week_vault + (len(set(six_week_tapes)))# How many uniqe tapes were vaulted in the last 6 weeks?
    six_week_average = six_week_vault // 6                      # Whole number division

# Find media in use for over 45 days
    from datetime import datetime, timedelta
    six_weeks_ago_date = (datetime.now() - timedelta(days = 46)).strftime('%m/%d/%Y')   # 46 days is "over" 45 days ago
    cmd = "/usr/openv/netbackup/bin/admincmd/bpimagelist -d 01/01/2000 -e " + six_weeks_ago_date + " -media -U"    # Get a list media older than 46 days
    args = shlex.split(cmd)                                     # Formats the string to be used with Popen - splits o
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        if "no entity was found" not in error:                  # No entries is a good thing
            raise ValueError(error)                             # Pass the Popen error

    nb_media_over = 0                                           # Initialize nb media overstay count
    for line in output.splitlines():                            # Search through lines of output
        if(majority_media in line):
            nb_media_over += 1

    return [Hostname, majority_media, media_seen, scratch_media, one_week_vault, six_week_average, media_in_use, nb_media_over]


########################################################################
#   __Main__
# Run only if local, not if called.
########################################################################


if __name__ == '__main__':                              # Execute only if ran locally
    from whereami import has_tape_library               # Local script to test if we have a tape library
    if has_tape_library():                              # Only run this stuff if we have a tape library
        from column import indent                           # Local script that prints in columns

#   *** Print the robot status
        print "*** Robot Status ***"
        status = library_status()
        for line in status:
            print line[0]

        print                                               # Print a seperator between function calls

#   *** Print the drive status
        print "*** Drive Status ***"
        try:
            status = drive_status()
        except ValueError as error:
            raise ValueError(error)                         # Stop work, Pass the error up to the next level

        labels = ('Drive Name', 'Server', 'Dr#', 'Device', 'Status')
        print indent([labels]+status, hasHeader=True)

        print                                              # Print a seperator between function calls

#   *** Check each robot/library
        connections = get_robot_connections()
        for line in connections:
            if line[1] != "No":                             # No invalid robot found

#   *** Inventory each library
                library_name = get_library_name (line[0], line[2])  # Send robot number, host name
                print "Inventorying", library_name
                try:
                    do_inventory (line[0], line[2])             # Run an inventory
                except ValueError as error:                     # Don't run any more. Stop and report
                    print "*** Inventory failed !!! ***"
                    print error
                    print
                else:                                           # Run the rest of there AREN'T any failure

#   *** List scratch in each library
                    scratch = list_scratch (line[0])            # Figure number of scrach in each TLD
                    print "scratch in", library_name, "is", scratch     # Print number of scratch in that TLD

#   *** List free slots of each library
                    f_slots = free_slots (line[0], line[2])     # Get number of free slots
                    print "Empty slots in", library_name, "is", f_slots         # Print free slots

                    print                                       # White space between robots

#   *** List scratch media available for recall
        print "*** Scrach available for recall ***"
        media = recallable_media()
        for line in media:
            print line

        print                                               # White space between robots

#   *** Get tape usage information
        print "*** Tape Usage ***"

        usage = tape_usage()
        print
        print "Domain:", usage[0]
        print "Majority tape label is:", usage[1]
        print "Majority Media seen:", usage[2]
        print "Majority media scratch:", usage[3]
        print "Last week vault:", usage[4]                     # Print one week vault
        print "Average vault:", usage[5]            # Print 6 week average
        print "  EBSO identified media: "
        print "    EBSO in use media: "
        print "      90 day tapes: "
        print "      6 week tapes:"
        print "      35 day tapes: "
        print "      EBSO tapes out of date "
        print "    EBSO expired media:"
        print "NB identified media:", usage[2]
        print "  NB in use media:", usage[6]
        print "    NB tapes out of date", usage[7]
        print "  NB scratch media:", usage[3]
        print
        print "For Excel Cut And Paste"
        print usage[2]      # Majority Media seen
        print usage[3]      # Majority media scratch
        print usage[4]      # Last week vault
        print usage[5]      # Average vault
        print               # EBSO Identified
        print               # EBSO in use
        print               # 90 dy tapes
        print               # 6 week tapes
        print               # 35 day tapes
        print               # EBSO Out of date
        print               # EBSO Expired media
        print usage[2]      # NB identified media
        print usage[6]      # NB in use media
        print usage[7]      # NB tapes out of date
        print usage[3]      # NB scratch media

    else:
        print "No NB attached library"

# end nblibdr_test.py
