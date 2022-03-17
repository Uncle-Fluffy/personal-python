# This script scrapes an S3 bucket looking for files that were save in a particular date range
# it then reports them to a SNS topic
 
# 3/16/2022 Created by Terry Carter
 
########################################################################
# Init / Include
########################################################################
import datetime     # 
import time
import sys          # 
 
def lambda_handler(event, context):
    GetDate()
 
def GetDate():
    #print ("Number of arguments:", len(sys.argv), "arguments")
    #print ("Argument List:", str(sys.argv))
 
    if len(sys.argv) == 7:      # if start and end dates are given
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        start_date = (str(datetime.datetime(year, month, day)) + "+00:00")
        print(start_date)

        year2 = int(sys.argv[4])
        month2 = int(sys.argv[5])
        day2 = int(sys.argv[6])
        end_date = (str(datetime.datetime(year2, month2, day2)) + "+00:00")
        print(end_date)
 
    elif len(sys.argv) == 4:    # if just the start date is given
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
    #     start_date = utc.localize(datetime.datetime(year, month, day))
        start_date = (str(datetime.datetime(year, month, day)) + "+00:00")
       # end_date = start_date + datetime.timedelta(days=1)
       #end_date = (time.strftime('%Y-%m-%d', (str(datetime.datetime(year, month, day))- 86400)))
        # foo = str(datetime.datetime(year, month, day))
        # print("foo", foo)
        # print(type(foo))
        # foo2 = datetime.datetime(year, month, day) + datetime.timedelta(days=1)
        # print("foo2", foo2)
        # print(type(foo2))
        # foo3 = str(datetime.datetime(year, month, day) + datetime.timedelta(days=1)) + "+00:00"
        # print("foo3", foo2)
        # print(type(foo3))
        end_date = str(datetime.datetime(year, month, day) + datetime.timedelta(days=1)) + "+00:00"

        print(start_date)
        print(end_date)

    else:   # No date given - assume yesterday
        end_date = (time.strftime('%Y-%m-%d', time.gmtime()) + " 00:00:00+00:00")
        start_date = (time.strftime('%Y-%m-%d', time.gmtime(time.time() - 86400))+ " 00:00:00+00:00")
 
    # Print year, month, day, hour, minute, second, microsecond, and tzinfo.
    print('start_date: {}'.format(start_date))
    print('end_date: {}'.format(end_date))
 
if __name__ == '__main__':
    GetDate()
