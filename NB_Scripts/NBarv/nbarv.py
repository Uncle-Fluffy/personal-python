#!/usr/bin/python
# nbarv.py
#
# Author: Terry Carter
# Creation: 4/9/2018
#
# This utility Adds, Removes and Verifies hostnames in NetBackup
#
########################################################################
#
# Requests for next version:
# 2) After adding host, validate that we can communicate to it.
#   bpclntcmd -hn on client to verify communication
#   blclntcmd -pn - verbose from admin box
#
# 5) Add tests to see what DC the host name refers to as well as sod, hod, rod, cod fod whatever
# 6) add host:
# Look for alpha neumeric a-z, A-Z, 0-9 and dash. No ; for example
# 8) File_validate
# Check and see if I have permissions to even open or write to the file
# 9) main
# Test to see if netbackup is up or not. If it's not up, let the user know and tell them to go away
# netbackup status


########################################################################
# Init / Include
########################################################################
import sys          # Used for sys.argv to determine starting flags
import subprocess   # Used for Popen, directions to the command line
import shlex        # used to format lines for Popen
import re           # Used for regular expression tests
import getpass      # Used to find the username

# file_location = '/usr/openv/scripts'
ok_nbu = '/tmp/ok_nbu.tmp'
add_nbu = '/tmp/add_nbu.tmp'
del_nbu = '/tmp/del_nbu.tmp'


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
# Check_Policy
# Checks to see if a given policy name is available
# Returns if found (0) or not (1)
########################################################################


def check_policy(policy_name):
    output = get_policies()
    output = output.splitlines()    # Splits multiple line var into one line per array element
    for line in output:             # For each line in the array
        if line == policy_name:
            return 0                # Policy name found
    return 1                # Policy name not found


########################################################################
# Get_HostName
# Polls for user input for the host name
# Tests for length and for 'p' placement in the name (Required for Windows boxes)
# Returns host name
########################################################################


def get_hostname(prompt):
    if len(sys.argv) > 2:                           # Does have a second argument
        host_name = sys.argv[2]
    else:                                           # If not, ask for one
        host_name = raw_input(prompt)

    if (host_name[2:4] == 'JD') or (host_name[2:4] == 'jd'):  # JD host names are shorter
        if len(host_name) < 10:  # Make sure the name is long enough
            raise ValueError("Name given is not a valid Windows host name - Too short. Must be at least 10 characters")
    else:
        if len(host_name) < 11:                         # Make sure the name is long enough
            raise ValueError("Name given is not a valid Windows host name - Too short. Must be at least 11 characters")

    if len(host_name) > 17:                         # Make sure the name is long enough
        raise ValueError("Name given is not a valid Windows host name - Too long. Must be less than 18 characters")

    if (host_name[2:4] == 'JD') or (host_name[2:4] == 'jd'):  # JD host names are shorter
        if not ((host_name[8:9] == 'P') or (host_name[8:9] == 'p')):  # Check for windows host name
            raise ValueError("Name given is not a valid Windows host name - Missing 'P' in 9th location")
    else:
        if not ((host_name[9:10] == 'P') or (host_name[9:10] == 'p')):  # Check for windows host name
            raise ValueError("Name given is not a valid Windows host name - Missing 'P' in 10th location")
        # raise Exception("Name given is not a valid Windows host name - Missing 'P' in 10th location")

    if not re.match("^[A-Za-z0-9]*$", host_name):
        raise ValueError("Name given is not valid. Must include a-z and 0-9 only")

# Add tests to see what DC the host name refers to as well as sod, hod, rod, cod fod whatever

    return host_name


########################################################################
# Get_Policy_Name
# Input host name
# Determine if it's CRM
#   If CRM, choose CRM policy if available
#   If not, choose default policy
# Determine if default policy is available
# Return policy name to use
########################################################################


def get_policy_name(host_name):
    if (host_name[2:5] == 'SOM') or (host_name[2:5] == 'som'):  # Check for SOM/CRM host name
        valid_policy = check_policy('NBU_images_CRM')  # NBU_images_CRM
        if valid_policy == 0:
            return 'NBU_images_CRM'
        else:
            valid_policy = check_policy('NBU_images')  # NBU_images
            if valid_policy == 0:
                return 'NBU_images'
            else:
                raise ValueError("No valid policy name found")

    else:                                               # Not a CRM Host
        valid_policy = check_policy('NBU_images')       # NBU_images
        if valid_policy == 0:
            return 'NBU_images'
        else:
            raise ValueError("No valid policy name found")


########################################################################
# Add_Host (to a Policy)
# (2018-04-17 2:10:32 PM) terry.carter: you CAN'T determine if a windows box is CRM JUST because of the name
# (2018-04-17 2:10:34 PM) terry.carter: Correct?
# (2018-04-17 2:10:54 PM) ramakrishnan.mahadevan@oracle.com: wrong.. any xxSOMXxxxx is CRM
########################################################################


def add_host():
    print '  Add Host'
    try:
        host_name = get_hostname("    Host name to add?> ")                      # Get a host name to add
    except ValueError as error:
        raise ValueError(error)                         # Stop work, Pass the error up to the next level
    policy_name = get_policy_name(host_name)            # Get a policy name based on the host name
    host_name = host_name.lower()

    try:
        host_name = find_running_hostname(host_name)
    except:
        pass                                            # find_running_hostname throws an exception if it's NOT found
    else:
        err = "Policy already found for " + host_name
        raise ValueError(err)

    if '-' not in host_name:                            # Check for -nfs or other extension like -bkp
        host_name = host_name + '-nfs'

    cmd = "/usr/openv/netbackup/bin/admincmd/bpplclients " + policy_name + " -add " + host_name + " Windows Windows"
    args = shlex.split(cmd)                             # Shlex allows to read the spaces on the cmd line.
    print cmd
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error
    else:
        print host_name, "was successfully added to the policy", policy_name
        return 0


# Note: for adding in bulk;
#
# Take the monthly AD list and sort by data center
# Create a one column list - I saved it to /home/tscarter/foo
# Run the verify
# /usr/openv/scripts/nbarv.py verify /home/tscarter/foo
# From the verify, capture the hosts to be added and save that, in this case to /home/tscarter/fooadd
# for i in $(cat /tmp/add_nbu.tmp); do /usr/openv/scripts/nbarv.py add $i ; done


########################################################################
# Find Running Host Name
# Takes in a given host name and compares to a list of running host names
# Returns the full host name that was found running
########################################################################


def find_running_hostname(host_name):
    cmd = "/usr/openv/netbackup/bin/admincmd/bpplclients"
    args = shlex.split(cmd)                             # Shlex allows to read the spaces on the cmd line.
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error

    for word in shlex.split(output):
        if re.search(host_name, word, re.IGNORECASE):
            return word                                 # Return found hosts name

    raise ValueError("No valid policy name found")


########################################################################
# Find_Policy
# Find the policy name(s) for a given host name
# /usr/openv/netbackup/bin/admincmd/bppllist -byclient ABSODACMEP12-nfs | grep "CLASS "
# CLASS NBU_images *NULL* 0 772000 0 *NULL*
# Returns the Policy Name
########################################################################


def find_policy(host_name):
    cmd = "/usr/openv/netbackup/bin/admincmd/bppllist -byclient " + host_name
    args = shlex.split(cmd)                                     # Shlex allows to read the spaces on the cmd line.
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    if error:
        raise ValueError(error)                         # Pass the Popen error

    output_list = output.split()                                # Split the output into an array
    policy_name = output_list[output_list.index('CLASS') + 1]   # Get the word AFTER "CLASS"

    return policy_name


########################################################################
# Remove Host (from Policy)
# Requests host name in from the command line or prompts for it.
# Requests the policy name for the host name
# Deletes the host name from the policy.
# Returns (0)
########################################################################


def remove_host():
    print '  Remove Host'
    try:
        host_name = get_hostname("    Host name to remove?> ")                      # Get a host name to add
    except ValueError as error:
        raise ValueError(error)                         # Stop work, Pass the error up to the next level

    if '-' not in host_name:                            # Check for -nfs or other extension like -bkp
        host_name = host_name + '-'
    host_name = find_running_hostname(host_name)
    policy_name = find_policy(host_name)

# We need to search for the host name. If the host name includes -nfs or -bkp or whatever, we're good
# but if the host name does not include the path, we need to do more of a wildcard search.
# There can be a problem when the host name ends in "p1" and you end up finding "p11, p12, p13" as well.
# Adding a "-" after the given host name will prevent that. "p1" -> "p1-"

    cmd = "/usr/openv/netbackup/bin/admincmd/bpplclients " + policy_name + " -delete " + host_name + " Windows Windows"
    args = shlex.split(cmd)                             # Shlex allows to read the spaces on the cmd line.
    print cmd
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error
    else:
        print host_name, "was successfully removed from the policy", policy_name
        return 0


# Note: for removing in bulk;
#
# Take the monthly AD list, view by data, filter, select by data center, select description - active
# Create a one column list - I saved it to /home/tscarter/foo
# Run the verify
# /usr/openv/scripts/nbarv.py verify /home/tscarter/foo
# Verify function will create /tmp/del_nbu.tmp
# for i in $(cat /tmp/del_nbu.tmp | grep -v "\."); do /usr/openv/scripts/nbarv.py remove $i ; done


########################################################################
# Get_Hosts_from_NBU
# Requests a list of hosts names from NBU
# Parses the result for just the host names
# Returns a simple list of host names
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

    return nbu_hosts


########################################################################
# Single_Validate
# Given a host name in question and a list of running host names
# returns if the given host name was found in the running list
########################################################################


def single_validate(host_name, nbu_hosts):
    for word in shlex.split(nbu_hosts):
        if re.search(host_name, word, re.IGNORECASE):   # Search for host name in list case insensitive
            return 0, word, 'Found'                      # When found, return
    return 1, host_name, 'Not found'                     # Default if not found


########################################################################
# File_Validate
# Given a file name and a list of running host names
# Compares the two lists and comes up with three possibilities
# 1) Given host name is running in NBU (OK)
# 2) Given host name is not running in NBU (Needs to be added)
# 3) Host name is running in NBU but not given/searched for (Needs to be deleted)
# Host names are added to one of three temporary files
# Results are printed out
########################################################################


#    Check and see if I have permissions to even open or write to the file

def file_validate(file_name, nbu_hosts):
    host_names = [line.rstrip('\n') for line in open(file_name)]   # Input host names and strip extra newlines
    ok_nbu_file = open(ok_nbu, "w+")                # Open the result files for write and read
    add_nbu_file = open(add_nbu, "w+")
    del_nbu_file = open(del_nbu, "w+")

    for line in host_names:                        # Checks if input hosts are have policies in NBU
        if line.strip():                            # Check for empty string
            status, host, found = single_validate(line, nbu_hosts)
            if status == 0:
                ok_nbu_file.write(host + '\n')      # add to the OK list
            else:
                add_nbu_file.write(host + '\n')     # add to the add list

    # '*** Reversing the test ***'
    string_input_lines = '\n'.join(host_names)     # convert from list to string
    list_nbu_hosts = nbu_hosts.split()              # convert from string to list

    for line in list_nbu_hosts:                     # Checks if host in NBU were searched for
        if re.search("-", line):                    # if the name has a - like "-nfs"
            #line,nfs=line.split("-")                # then just geet the host name out of it
            line = line.split("-")[0]               # then just get the host name out of it
        status, host, found = single_validate(line, string_input_lines)
        #status, host, found = single_validate(host_only, string_input_lines)
        if status == 1:
            del_nbu_file.write(host + '\n')         # add to the delete list

    ok_nbu_file.seek(0)                             # Rewind pointers to the beginning of the files
    add_nbu_file.seek(0)
    del_nbu_file.seek(0)

    print
    print 'Currently in active policies'
    print ok_nbu_file.read()

    print
    print 'Add these hosts to NBU'                  # Print the findings
    print add_nbu_file.read()

    print
    print 'Delete these hosts from NBU'
    print del_nbu_file.read()

    ok_nbu_file.close()
    add_nbu_file.close()
    del_nbu_file.close()
    return 0


########################################################################
# Validate_host
# Determines if there was a second argument given in requesting validation
# (I.E. host name or file path)
# If not, it requests name or path
# If input is a pathname, request sent to file_validate to compare files
# Otherwise assumes input is a host name or part of a host name and searches individually
########################################################################


def validate_host():
    print '  Validate Host'

    if len(sys.argv) > 2:                               # Does have a second argument
        host_name = sys.argv[2]
    else:                                               # If not, ask for one
        host_name = raw_input("  Host name, or file path?: ")

    if len(host_name) < 5:                              # Make sure the name is long enough
        raise ValueError("Name given is not a valid Windows host name or path - Too short")

    nbu_hosts = get_hosts_from_nbu()                    # Get a list of host currently assigned to policies

    # Do a single check if a single name is submitted. Do a full check if a file is sent.
    if '/' in host_name:                                # Is not a path
        file_validate(host_name, nbu_hosts)
    else:
        if '-' not in host_name:                        # Check for -nfs or other extension like -bkp
            host_name = host_name + '-'                 # adds '-' to make sure we get the right host
        status, host, found = single_validate(host_name, nbu_hosts)     # Search for host_name in nbu_hosts
        if status == 0:
            print host, found
        else:
            err = "Host name " + host_name + " not found"
            raise ValueError(err)

    return 0


########################################################################
# Main
########################################################################


# Test to see if netbackup is up or not. If it's not up, let the user know and tell them to go away
# netbackup status

username = getpass.getuser()            # Check and see if you're logged in as root. If not deny service
if username != 'root':
    print "Must be logged in as root"
    sys.exit(1)

# bptestbpcd to test if the connection deamon is listening

"""
user_options = {
    'add': add_host(),
    'remove': remove_host(),
    'verify': validate_host()
}

try:
    pass
except KeyError:
    print "not found"
except ValueError as err:
    print err
    sys.exit(1)
sys.exit(0)
"""

if len(sys.argv) > 1:                   # If we typed in more than just the script name
    try:
        if sys.argv[1] == 'add':
            add_host()
        elif sys.argv[1] == 'remove':
            remove_host()
        elif sys.argv[1] == 'verify':
            validate_host()
        else:
            print "   !! '" + sys.argv[1] + "' unknown command"
            print "   Usage: [add|remove|verify] [host|file name]"
    except ValueError as err:
        print err
        sys.exit(1)                     # Completed with errors
    sys.exit(0)                         # Completed with no errors
else:                                   # Go into interactive mode
    action = ""
    while action not in ['exit', 'quit']:
        action = raw_input("  nbarv> ")
#    add more verbose prompt like
#    Display what? (library/volume/drive/initiator/target/mapping/quit)> drive
        try:
            if action == 'add':
                add_host()
            elif action == 'remove':        # Synonym delete
                remove_host()
            elif action == 'verify':        # Synonym Validate
                validate_host()
            elif action == 'help':
                print
                print "  usage: [add|remove|verify] [help|quit|exit]"
        except ValueError as err:
            print err


