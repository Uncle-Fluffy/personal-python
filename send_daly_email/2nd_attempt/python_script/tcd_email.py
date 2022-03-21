# This script scrapes an S3 bucket looking for files that were save in a particular date range
# it then reports them to a SNS topic
# Core code from Connor Reid
# 3/16/2022 Modified by Terry Carter
 
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
    start_date, end_date = GetDate()
    s3, sns = boto3_session_lambda()
    files_found_txt = get_new_filenames(s3, start_date, end_date)
    send_email(sns, files_found_txt)

########################################################################
# GetDate()
########################################################################

def GetDate():
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
        start_date = datetime.datetime.strptime((str(datetime.datetime(year, month, day)) + "+00:00"), '%Y-%m-%d %H:%M:%S%z')
        end_date = datetime.datetime.strptime((str(datetime.datetime(year, month, day) + datetime.timedelta(days=1)) + "+00:00"), '%Y-%m-%d %H:%M:%S%z')

    else:   # No date given - assume yesterday
        start_date = datetime.datetime.strptime((time.strftime('%Y-%m-%d', time.gmtime(time.time() - 86400))+ " 00:00:00+00:00"), '%Y-%m-%d %H:%M:%S%z')
        end_date = datetime.datetime.strptime((time.strftime('%Y-%m-%d', time.gmtime()) + " 00:00:00+00:00"), '%Y-%m-%d %H:%M:%S%z')

    # Print year, month, day, hour, minute, second, microsecond, and tzinfo.
    print('start_date: {}'.format(start_date))
    print('end_date: {}'.format(end_date))
    return start_date, end_date

#########################################################################
# boto3_session_main
#########################################################################

def boto3_session_main():
    session = boto3.Session(profile_name='exp-devsecops')
    s3 = session.client('s3', region_name='us-west-2')
    sns = session.client('sns', region_name='us-east-1')
    return s3, sns

#########################################################################
# boto3_session_lambda
#########################################################################

def boto3_session_lambda():
    bucket_name = 'exptransmission'
    s3 = boto3.client('s3', region_name='us-west-2')
    sns = boto3.client('sns', region_name='us-east-1')
    return s3, sns

########################################################################
# human_readable_size
########################################################################

def human_readable_size(size, decimal_places=0):
    for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return str(f"{size:.{decimal_places}f} {unit}")

########################################################################
# get_new_filenames
########################################################################

def get_new_filenames(s3, start_date, end_date):
    bucket_name = 'exptransmission'
    paginator = s3.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucket_name)
    count = 0
    files_found_txt = ""
    page_list = []

    # get everything in S3 bucket
    for page in page_iterator:
        if 'Contents' in page:
            page_list.append(page)

    # do the search
    for page in page_list:
        for obj in page['Contents']:
            obj_size = obj['Size']
            last_modified = obj['LastModified']
            if start_date < last_modified < end_date:
                obj_key = obj['Key']
                idx = obj_key.rfind('/')
                object_name = obj_key[idx + 1:len(obj_key)] 
                try:
                    files_found_txt += (datetime.datetime.strftime(last_modified, '%Y-%m-%d %H:%M:%S%z')) # Add modification date stamp
                    for i in range(11 - (len(human_readable_size(obj_size)))): # pre-pad for size
                        files_found_txt += ' '
                    files_found_txt += human_readable_size(obj_size) # Add file size
                    files_found_txt += ' ' + object_name # add file name
                    files_found_txt += '\r\n' # Add carriage return/line feed

                except Exception as e:
                    print("Exception***")
                    print(last_modified)
                    print(object_name)
                    print(e)
                count = count + 1

    print('count: {}'.format(count))
    print(files_found_txt)
    return(files_found_txt)

########################################################################
# send_email
########################################################################

def send_email(sns, files_found_txt):
    topic_arn = 'arn:aws:sns:us-east-1:204048894727:test-tcd-daily-email'  # devsecops, change subscriptions for testers
    #topic_arn = 'arn:aws:sns:us-east-1:204048894727:tcd_daily_email'   # regular email to devops et. all
    print('topic_arn: {}'.format(topic_arn))
    subject = 'Wells Fargo TCD Dropbox'
    message = files_found_txt

    # if no files, then send email with no files
    if len(files_found_txt) == 0:
        message = 'There are no files for the past 24 hours.'

    response = sns.publish(
        TopicArn = topic_arn,
        Message = message,
        Subject = subject
    )

########################################################################
# __main__
########################################################################

if __name__ == '__main__':
    start_date, end_date = GetDate()
    s3, sns = boto3_session_main()
    files_found_txt = get_new_filenames(s3, start_date, end_date)
    send_email(sns, files_found_txt)
