#!/bin/sh

# Set date
yesterday_date=$(date -d "yesterday" '+%Y-%m-%d')
today_date=$(date -d "today" '+%Y-%m-%d')

# Copy all directory information to a file
aws s3 ls s3://exptransmission/wellsfargoexp/downloads/ --profile sandbox --human-readable --summarize > Wells_S3_Query.txt

# Check to see if there's any files for yesterday
contains_data=$(grep $yesterday_date Wells_S3_Query.txt)

# Depending on if there are files or not, send appropriate email with info
if [ ! "$contains_data"]
then
        echo "There are no files for the past 24 hours."

        # Send email to everyone subscribed to SNS topic.
        aws sns publish --topic-arn "arn:aws:sns:us-east-1:204048894727:tcd_daily_email" --subject "Wells Fargo TCD Dropbox" --message "There are no files for the past 24 hours"
else
        # Remove everything but yesterday's and today's files from the list.
        grep $yesterday_date Wells_S3_Query.txt > Wells_S3_Result.txt
        grep $today_date Wells_S3_Query.txt >> Wells_S3_Result.txt

        # Sort all contents by date descending
        sort -o Wells_S3_Result.txt Wells_S3_Result.txt -r

        # Print list to the screen
        cat Wells_S3_Result.txt

        # Send email to everyone subscribed to SNS topic.
        aws sns publish --topic-arn "arn:aws:sns:us-east-1:204048894727:tcd_daily_email" --subject "Wells Fargo TCD Dropbox" --message file://Wells_S3_Result.txt
fi