## daily ping

Send yourself a daily text of any reminders, errors, or status updates

I run this simple yet surprisingly useful script on my raspberry pi to send me the status of my pi and any reminders. Any input to the script will be sent as text message to your phone. It uses the textbelt.com API which provides 1 free text message a daily, hence the name. You can also provide a key if you want to send more frequently than that.

### usage
```
usage: ping.py [-h] [-f FILENAME] [-k KEY] -p PHONE [-n]

read message via either stdin or file to send as sms message

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        file of message to send, file is truncated on success
  -k KEY, --key KEY     textbelt api key, defaults to 'textbelt' (1 msg/day)
  -p PHONE, --phone PHONE
                        phone number with no spaces (ex. 5557727420)
  -n, --no-truncate     don't truncate message to fit single sms message limit
```

```
echo 'hello world' | daily-ping -p <your-phone-number>
```

### example

I invoke this script as a daily cron on my raspberry pi where it reads from a log file that my other cron jobs write to. Here's an example crontab file:
```
SHELL=/bin/bash

# monthly reminders
0 0 27 * * echo "send rent" >> /var/log/daily-ping.log
0 0 20 * * echo "pay credit card" >> /var/log/daily-ping.log

# check if pihole still running
0 0 * * *  pihole status | grep -q Enabled || echo "pihole down" >> /var/log/daily-ping.log

# check if disk almost full, send this one immediately if so
0 0 * * * df --output=pcent / | grep -q '[89][0-9]\%' && echo 'disk almost full' | daily-ping -p 5557727420

# apply any changes to this crontab file
0 1 * * * crontab -u pi /home/pi/crontab || echo "crontab fail" >> /var/log/daily-ping.log

# check for any updates to the daily ping script
0 0 * * * diff -q <(cat $(which daily-ping)) <(curl -sL https://raw.githubusercontent.com/mmercedes/daily-ping/ping.py) || echo 'update available' > /var/log/daily-ping.log

# send any log messages as your daily ping at 4:20
20 4 * * * daily-ping -f /var/log/daily-ping.log -p 5557727420
```

### install
Since its just one python file with no dependencies, you can just save the file somehwere in your `$PATH` and let it rip!
```
$ curl -sL -o daily-ping https://raw.githubusercontent.com/mmercedes/daily-ping/ping.py
$ sudo mv daily-ping /usr/local/bin/daily-ping && chmod +x /usr/local/bin/daily-ping
$ daily-ping -h
```

Optionally, you can save the example crontab file as a starting point, and edit it accordingly:
```
$ curl -L -o $HOME/crontab https://raw.githubusercontent.com/mmercedes/daily-ping/master/crontab.example
# make any changes to the file
$ nano crontab 
# setup your daily-ping to run
$ crontab -u $USER crontab
```
