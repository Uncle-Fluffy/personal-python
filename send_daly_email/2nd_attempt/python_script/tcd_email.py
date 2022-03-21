# This script scrapes an S3 bucket looking for files that were save in a particular date range
# it then reports them to a SNS topic
 
# 3/16/2022 Created by Terry Carter
 
########################################################################
# Init / Include
########################################################################
import sys          # For user input when ran directly
import datetime     # For date calculations        
import time         # For current date/time calculations
import boto3        # For access to AWS

########################################################################
# lambda_handler
########################################################################
  
def lambda_handler(event, context):
    GetDate()
    boto3_session_lambda()

########################################################################
# GetDate()
########################################################################

def GetDate():
    #print ("Number of arguments:", len(sys.argv), "arguments")
    #print ("Argument List:", str(sys.argv))
    tz = datetime.timezone.utc

    if len(sys.argv) == 7:      # if start and end dates are given
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        start_date = datetime.datetime.strptime((str(datetime.datetime(year, month, day)) + "+00:00"), '%Y-%m-%d %H:%M:%S%z')

        year2 = int(sys.argv[4])
        month2 = int(sys.argv[5])
        day2 = int(sys.argv[6])
        end_date = datetime.datetime.strptime((str(datetime.datetime(year2, month2, day2)) + "+00:00"), '%Y-%m-%d %H:%M:%S%z')
 
    elif len(sys.argv) == 4:    # if just the start date is given
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        #start_date = (str(datetime.datetime(year, month, day)) + "+00:00") # this gives a string output
        start_date = datetime.datetime.strptime((str(datetime.datetime(year, month, day)) + "+00:00"), '%Y-%m-%d %H:%M:%S%z')
        #end_date = str(datetime.datetime(year, month, day) + datetime.timedelta(days=1)) + "+00:00" # this gives a string output
        end_date = datetime.datetime.strptime((str(datetime.datetime(year, month, day) + datetime.timedelta(days=1)) + "+00:00"), '%Y-%m-%d %H:%M:%S%z')

    else:   # No date given - assume yesterday
        #end_date = (time.strftime('%Y-%m-%d', time.gmtime()) + " 00:00:00+00:00")
        #start_date = (time.strftime('%Y-%m-%d', time.gmtime(time.time() - 86400))+ " 00:00:00+00:00")
        start_date = datetime.datetime.strptime((time.strftime('%Y-%m-%d', time.gmtime(time.time() - 86400))+ " 00:00:00+00:00"), '%Y-%m-%d %H:%M:%S%z')
        end_date = datetime.datetime.strptime((time.strftime('%Y-%m-%d', time.gmtime()) + " 00:00:00+00:00"), '%Y-%m-%d %H:%M:%S%z')

    # Print year, month, day, hour, minute, second, microsecond, and tzinfo.

    print('start_date: {}'.format(start_date))
    print(type(start_date))
    print('end_date: {}'.format(end_date))
    print(type(end_date))
    # end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S%z') # This works to convert string into datetime.datetime
    return start_date, end_date

#########################################################################
# boto3_session_main
#########################################################################

def boto3_session_main():
    bucket_name = 'exptransmission'

    #session = boto3.session.Session(profile_name=profile)
    session = boto3.Session(profile_name='exp-devsecops')
    s3 = session.client('s3', region_name='us-west-2')
    sns = session.client('sns', region_name='us-east-1')
    # print('boto3_session_main')
    # print(s3)
    # print(type(s3))
    return s3, sns

#########################################################################
# boto3_session_lambda
#########################################################################

def boto3_session_lambda():
    #region = 'us-west-2'
    bucket_name = 'exptransmission'
    s3 = boto3.client('s3', region_name='us-west-2')
    sns = boto3.client('sns', region_name='us-east-1')
    # print('boto3_session_lambda')
    return s3, sns

########################################################################
# human_readable_size
########################################################################

def human_readable_size(size, decimal_places=0):
    for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

########################################################################
# get_new_filenames
########################################################################

def get_new_filenames(s3, start_date, end_date):
    print('start_date4:', start_date)
    print('end_date4:', end_date)
    bucket_name = 'exptransmission'
    paginator = s3.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucket_name)
    count = 0
    files_found = []
    page_list = []

    # get everything in S3 bucket
    for page in page_iterator:
        if 'Contents' in page:
            page_list.append(page)

    # print number of pages
    print('len(page_list): {}'.format(len(page_list)))

    # do the search
    for page in page_list:
        print('count: {}'.format(count))
        for obj in page['Contents']:
            obj_size = obj['Size']
            last_modified = obj['LastModified']
            #print('last_modified', last_modified)
            #print(type(last_modified))
            if start_date < last_modified < end_date:
                print() # blank line for clarity
                print('last_modified: {}'.format(last_modified))
                #print('obj_size: {}'.format(size(obj_size, system=alternative))) # toubleshooting line
                print('obj_size:', human_readable_size(obj_size)) # toubleshooting line
                obj_key = obj['Key']
                print('obj_key: {}'.format(obj_key)) # toubleshooting line
                idx = obj_key.rfind('/')
                object_name = obj_key[idx + 1:len(obj_key)]
                print('object_name: {}'.format(object_name))
                #r1 = object_name.split('_') # finds the box used
                #print(len(r1)) # toubleshooting line
                #print(r1) # toubleshooting line
                try:
                    #s1 = r1[2]
                    #print('s1', s1) # toubleshooting line
                    files_found.append(
                        {
                            'last_modified': last_modified,
                            #'obj_size': size(obj_size, system=alternative),
                            'obj_size': obj_size,
                            'object_name': object_name,
                        }
                    )
                except Exception as e:
                    print("Exception***")
                    print(last_modified)
                    print(object_name)
                    print(e)
                count = count + 1

    print('count: {}'.format(count))
    print('files_found', files_found)

    # future
    # change
    #   home_path = '/tmp/output-' + str(cur_date) + '.csv' 
    #   f = open(home_path, 'a')
    # to this
    # with open('/etc/passwd') as f:
    #   for line in f:
    #     print(line)



########################################################################
# __main__
########################################################################

if __name__ == '__main__':
    start_date, end_date = GetDate()
    print('start_date3:', start_date)
    print('end_date3:', end_date)
    s3, sns = boto3_session_main()
    get_new_filenames(s3, start_date, end_date)
