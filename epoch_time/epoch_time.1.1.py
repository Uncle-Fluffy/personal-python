#!/usr/bin/python
#
# Epoch Time
# Created: Terry Carter
# Date: 9/13/2019
#
# Tools used to converts a date to epoch date and back
#
version = "1.1"

# v1.0 9/13/2019 Base
# v1.1 9/26/2019 Creation of single string date like 20190926

########################################################################
#   Init / Include
########################################################################

import datetime
import time
import calendar
#import pytz

########################################################################
# Time Zone
#
# Return the time zone offset
#
########################################################################

def time_zone():
    if (time.localtime().tm_isdst == 0):                                # Are we on daylight savings?
        return time.timezone / -3600                                    # No, return standard time zone as hours
    else:
        return time.altzone / -3600                                     # Yes, return DST as hours


########################################################################
# Time Zone Name
#
# Return the text name of the current time zone
#
########################################################################

def time_zone_name():
#   print "Time Zone(s) ", time.tzname
    return time.tzname                                                  # Return the human readable time zone name


########################################################################
# Epoch to date
#
# Takes in an epoch time and returns a human readable date
#
########################################################################

def epoch_to_date(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp)              # Convert epoch time to human readable
    return dt_object

########################################################################
# Format Test Date
#
# Formatting a date into datetime.datetime object could be confusing
#   as well as needing to include libraries and such
#   Simple converter to use as part of this library
#
########################################################################
def format_test_date(test_year, test_month, test_day):
    return datetime.datetime(test_year, test_month, test_day)


########################################################################
# Date to Epoch
#
# Takes in a date and returns the epoch time for it.
#
########################################################################

def date_to_epoch(test_date):
    tz = time_zone()                                                    # Get the time zone shift in hours
    epoch_date = datetime.datetime(1970, 01, 01)
    timesince = test_date - epoch_date                                  # Subtract the epoch from the given date (difference)

    test_days = timesince.days                                          # Get the number of days difference
    test_seconds = timesince.seconds                                    # Get the number of seconds difference
    epoch_seconds = (test_days*24*60*60) + test_seconds - (tz*60*60)    # Convert days and seconds to seconds since the epoch

    return epoch_seconds


########################################################################
# This Morning
########################################################################

def this_morning():
    tz = time_zone()                                                    # Get the time zone shift in hours
    epoch_date = datetime.datetime(1970, 01, 01)                        # Set the epoch date
    today = datetime.datetime.today()                                   # Get today's date
    today_difference = today - epoch_date                               # Number of days since the epoch
    today_days = today_difference.days                                  # Extract the day count out
    today_epoch_seconds = (today_days *24*60*60) - (tz*60*60)           # strip the days only and make up for the time shift
    return today_epoch_seconds


########################################################################
# Yesterday Morning
########################################################################

def yesterday_morning():
    tz = time_zone()                                                    # Get the time zone shift in hours
    epoch_date = datetime.datetime(1970, 01, 01)                        # Set the epoch date
    today = datetime.datetime.today()                                   # Get today's date
    yesterday_difference = today - epoch_date - datetime.timedelta(days = 1)    # Number of days since the epoch -1 (yesterday)
    yesterday_days = yesterday_difference.days                          # Extract the day count out
    yesterday_epoch_seconds = (yesterday_days *24*60*60) - (tz*60*60)   # strip the days only and make up for the time shift
    return yesterday_epoch_seconds


########################################################################
#
# Single String
#
# Return the date as a single string like 20190928
#
########################################################################

def single_string_date():
    return (datetime.datetime.now().strftime("%Y%m%d"))


########################################################################
#   __Main__
# Run only if local, not if called.
########################################################################


if __name__ == '__main__':                                              # Execute only if ran locally
    print "Version:", version
    print "*** Epoch Time Library can give you the following information: ***"

    ### Time Zone ###
    tz = time_zone()                                                    # Get the time zone shift in hours
    print "System Time Zone ", tz

    ### Time Zone Name ###                                              # Print the time zone name
    tzn = time_zone_name()
    print "Time Zone Name", tzn

    ### Current Epoch Time ###                                          # Print the current time in epoch
    question_date = datetime.datetime.now()
    epoch = date_to_epoch(question_date)
    print
    print "Current epoch time is", epoch

    ### Epoch time to date ###                                          # Change an epoch time to human readable date
    epoch_time = 1568385622
    human_time = epoch_to_date(epoch_time)
    print
    print "Epoch Time", epoch_time ,"converts to human date", human_time

    ### Date to Epoch ###                                               # Find the ephoch time of a given date
    year = 1988
    month = 9
    day = 28
    formatted_date = format_test_date(year, month, day)
    epoch_date = date_to_epoch(formatted_date)
    print "The date", year, month, day, "Returned epoch time ", epoch_date

    ### This Morning ###                                                # Find the epoch time of this morning
    today_epoch_time = this_morning()
    print
    print "The epoch time at midnight this morning was", today_epoch_time

    ### Yesterday Morning ###                                           # Find the epoch time of yesterday morning
    yesterday_epoch_time = yesterday_morning()
    print "The epoch time at midnight yesterday morning was", yesterday_epoch_time

    ### Single String Date ###
    print
    print "Single String Date", single_string_date()

    ### Extras ###
    print
    print "To see the current epoch time in bash"
    print "date -d now +%s"
    print "To convert from epoch time to human time in bash"
    print "time date -d @ <epoch time>"

### End epoch_time ###
