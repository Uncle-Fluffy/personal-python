# This is a set of commands showing time functions in python 3.8
# Created by Terry Carter on 3/16/2022

#from asyncio import current_task
import datetime
import time

print("Current date/time")
current_time = time.localtime()
print ("current_time", current_time)                        # Print local current time '(tm_year=2022, tm_mon=3, tm_mday=16, tm_hour=13, tm_min=12, tm_sec=43, tm_wday=2, tm_yday=75, tm_isdst=1)'
print()

print("GMT's date/time")
gm_time = time.gmtime()
print("gm_time", gm_time)                                   # Print GMT current time '(tm_year=2022, tm_mon=3, tm_mday=16, tm_hour=18, tm_min=12, tm_sec=43, tm_wday=2, tm_yday=75, tm_isdst=0)'
print(time.strftime('%Y-%m-%d', gm_time))                   # Print GMT current date only '2022-03-16'
print(time.strftime('%Y-%m-%d', gm_time), "00:00:00+00:00") # Print GMT current date zero'd time  '2022-03-16 00:00:00+00:00'
oneline_gm_time = (time.strftime('%Y-%m-%d', time.gmtime()) + " 00:00:00+00:00") # 2022-03-16 00:00:00+00:00
print('oneline_gm_time', oneline_gm_time)
print()

print("Yesterday's date")
yesterday_gm_time = time.gmtime(time.time() - 86400)
print(time.strftime('%Y-%m-%d', yesterday_gm_time), "00:00:00+00:00") # Print yesterday's date, zero'd time '2022-03-15 00:00:00+00:00'
oneline_yesterday_gm_time = (time.strftime('%Y-%m-%d', time.gmtime(time.time() - 86400))+ " 00:00:00+00:00") # 2022-03-15 00:00:00+00:00
print("oneline_yesterday_gm_time", oneline_yesterday_gm_time)
print()

print('string to date conversion')
# Converting input dates as a string
year = "2022"
month = "3"
day = "16"
date_string = year + " " + month + " " + day        # Convert individual strings to one string
print(date_string)                                  # 2022 3 16
manual_date = time.strptime(date_string, '%Y %m %d')   # (tm_year=2022, tm_mon=3, tm_mday=16, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=2, tm_yday=75, tm_isdst=-1)
print("manual_date as a string", manual_date)
print(time.strftime('%Y-%m-%d', manual_date), "00:00:00+00:00") # 2022-03-16 00:00:00+00:00
print()

print('int to date conversion')
# Converting input dates as a string
year2 = 2022
month2 = 3
day2 = 16
int_manual_date = datetime.datetime(year2, month2, day2)
print (int_manual_date)
print (str(int_manual_date) + "+00:00")             # 2022-03-16 00:00:00+00:00
print()