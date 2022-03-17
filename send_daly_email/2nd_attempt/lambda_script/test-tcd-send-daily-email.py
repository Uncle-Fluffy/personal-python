    # This script scrapes an S3 bucket looking for files that were save in a particular date range
    # it then reports them to a SNS topic

# 3/16/2022 Created by Terry Carter

########################################################################
# Init / Include
########################################################################
import datetime     # 
import sys          # 
import pytz         # Used for utc.localize
utc = pytz.UTC

def lambda_handler(event, context):
    GetDate()

def GetDate():
    print ("Number of arguments:", len(sys.argv), "arguments")
    print ("Argument List:", str(sys.argv))

    if len(sys.argv) == 7:      # if start and end dates are given
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        start_date = utc.localize(datetime.datetime(year, month, day))

        year2 = int(sys.argv[4])
        month2 = int(sys.argv[5])
        day2 = int(sys.argv[6])
        end_date = utc.localize(datetime.datetime(year2, month2, day2))

    elif len(sys.argv) == 4:    # if just the start date is given
        year = int(sys.argv[1])