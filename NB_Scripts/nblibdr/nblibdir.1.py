#!/usr/bin/python
#
# nblibdr.py
#
# This script checks the health and status of the library and drives on a NBU environment
#
#
# Created: Terry Carter
# Date: 1/16/2019
#
version = "1.0"

########################################################################
#   Init / Include
########################################################################


import subprocess                                       # Used for Popen, directions to the command line
import shlex                                            # used to format lines for Popen


########################################################################
#
#   get_media_servers
#  Gets a list of media servers
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

    return return_servers                               # Return a list of servers


########################################################################
# drive_status
# show status of drives
# /usr/openv/volmgr/bin/vmoprcmd
# /usr/openv/volmgr/bin/tpconfig
#
########################################################################


def drive_status():
    dev_dict = {}
    dev_array = []

    try:
        server_list = get_media_servers()                       # Get a list of media servers
    except ValueError as error:
        raise ValueError(error)                                 # Stop work, Pass the error up to the next level

    for server in server_list.splitlines():
        cmd = "/usr/openv/volmgr/bin/vmoprcmd -dp -h " + server # Insert whatever bp command you want to run here
        args = shlex.split(cmd)                                 # Formats the string to be used with Popen - splits o
        output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if error:
            raise ValueError(error)                             # Pass the Popen error

        for lines in output.splitlines():                       # list through output
            if lines != "":                                     # Ignore blank lines
                if lines.split()[0].isdigit():                  # 1st item on the line is a digit
                    if "dev" in lines.split()[1]:               # 2nd item has the word dev in it
                        dev_dict.update({server  + " " + lines.split()[0] : lines.split()[1] + " " + lines.split()[2]})
                    else:                                       # It's a drive name
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
# Get robot connections
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

    return status_array                                         # Return findings


########################################################################
#   __Main__
# Run only if local, not if called.
########################################################################


if __name__ == '__main__':                              # Execute only if ran locally
    from column import indent                           # Local script that prints in columns

#   Print the robot status
    status = library_status()
    for line in status:
        print line[0]

    print

#   Print the drive status
    try:
        status = drive_status()
    except ValueError as error:
        raise ValueError(error)                         # Stop work, Pass the error up to the next level

    labels = ('Drive Name', 'Server', 'Dr#', 'Device', 'Status')
    print indent([labels]+status, hasHeader=True)
