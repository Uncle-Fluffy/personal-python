# send_daily_email

## Install

    $ pip install -r requirements.txt

## Run
    # For a window of time
    $ python main.py start_year start_month start_day end_year end_month end_day

    # For a single day in history
    $ python main.py start_year start_month start_day

    # For yesterday
    $ python main.py
    
## Example
    # For a window of time    
    # list files for Jan 14th through the 18th, 2022
    $ python main.py 2022 1 14 2022 1 19

    # For a single day in history
    # list files for Jan 14th, 2022    
    $ python main.py 2022 1 14

    # For yesterday
    $ python main.py