#!/usr/bin/python
#
# nbjobs.py
#
# This script looks at the length of jobs running in the NBU environment
#
#
# Created: Terry Carter
# Date: 1/16/2019
#
version = "1.2"
# v1.2 12/13/2019 Added scrape all columns
# v1.1 9/24/2019  Added scrape most columns
# v1.0 1/16/2019  Origional

########################################################################
#   Init / Include
########################################################################


import subprocess                                       # Used for Popen, directions to the command line
import shlex                                            # used to format lines for Popen
max_job_time = 24                                       # Max Job Time in hours


########################################################################
#
#   Scrape
# Just get the raw job informaion from NBU
#
########################################################################


def scrape():
    cmd = "/usr/openv/netbackup/bin/admincmd/bpdbjobs -gdm" # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                                 # Formats the string to be used with Popen - splits on spaces
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error
    else:
        return output


########################################################################
#
#   Scrape Most Columns
# Just get the raw job informaion from NBU
#
########################################################################


def scrape_most():
    cmd = "/usr/openv/netbackup/bin/admincmd/bpdbjobs -most_columns" # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                                 # Formats the string to be used with Popen - splits on spaces
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error
    else:
        return output


########################################################################
#
#   Scrape All Columns
# Just get the raw job informaion from NBU
#
########################################################################


def scrape_all():
    cmd = "/usr/openv/netbackup/bin/admincmd/bpdbjobs -all_columns" # Insert whatever bp command you want to run here
    args = shlex.split(cmd)                                 # Formats the string to be used with Popen - splits on spaces
    output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error:
        raise ValueError(error)                         # Pass the Popen error
    else:
        return output



########################################################################
#
#   Parse
# Parse out the different fields
# Compare if any job is running over max_job_time
# Return those jobs
#
########################################################################


def parse_jobs(max_job_time):
    try:
        raw_jobs = scrape()                             # Get a list of NBU jobs
    except ValueError as error:
        raise ValueError(error)                         # Stop work, Pass the error up to the next level

    job_array = []                                      # Initialize array
    for line in raw_jobs.splitlines():                  # Look through every job
        field = line.split(",")                         # Split every field in the line
        if field[2] == "1":                             # 1=pending, 2=waiting, 3=complete
            backup_hours = int(field[9])/3600
            if backup_hours > max_job_time:             # Job has ran too long
                job_array.append([field[6],field[0],backup_hours])      # Add it to the list

    return job_array


########################################################################
#   __Main__
# Run only if local, not if called.
########################################################################


if __name__ == '__main__':                              # Execute only if ran locally
    job_time = 24                                   # Max Job Time in hours
    long_jobs = parse_jobs(job_time)

    if long_jobs == []:
        print "All jobs running normally"
    else:
        for line in long_jobs:                          # Read through all the lines
            print "Host", line[0] , ", Backup job", line[1], ", has been running for over", line[2], "Hours"

### end nbjobs.py ###
