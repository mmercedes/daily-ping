#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode

# replace with your key if you want to avoid adding it via the command line
KEY = "textbelt"

ENDPOINT = "https://textbelt.com/text"
RETRIES = 3
TIMEOUT = 10
# https://textbelt.com/faq
# "The maximum size of a text is 140 bytes."
SMS_MSG_LIMIT = 140
API_MSG_LIMIT = 1024


def parse_args():
    parser = argparse.ArgumentParser(description="read message via either stdin or file to send as sms message via textbelt.com")
    parser.add_argument("-f", "--filename", help="file of message to send, file is truncated on success")
    parser.add_argument("-k", "--key", help="textbelt api key, defaults to 'textbelt' (1 msg/day)", default=KEY)
    parser.add_argument("-p", "--phone", help="phone number with no spaces (ex. 5557727420)", required=True)
    parser.add_argument("-n", "--no-truncate", help="don't truncate message to fit single sms message limit", default=False, action='store_true')

    args = parser.parse_args()

    is_pipe = not os.isatty(sys.stdin.fileno())

    msg = ""
    # messages via stdin
    if is_pipe:
        msg = sys.stdin.read()
    # messages from file
    elif args.filename:
        # fail if file doesnt exist
        with open(args.filename, "rt+") as file:
            msg = file.read()
            file.seek(0)
            file.truncate()
    else:
        parser.print_help(file=sys.stderr)
        exit(1)

    return args, msg


def post(key, phone, msg):
    data = {
        'key': key,
        'message': msg,
        'phone': phone
    }

    try:
        data = urlencode(data).encode()
        req = Request(ENDPOINT, data=data)

        resp = urlopen(req, timeout=TIMEOUT)
        error = ""
        for i in range(RETRIES):
            body = json.loads(resp.read())
            success = resp.status == 200 and body.get("success", False)
            error = body.get("error", "")

            if success:
                return ""

            time.sleep(1)
            resp = urlopen(req, timeout=TIMEOUT)

        return "%d %s  %s" % (resp.status, resp.reason, error)
    except Exception as e:
        return str(e)


def main():
    args, msg = parse_args()

    if len(msg) == 0:
        print("nothing to send")
        exit(0)

    # truncate text to fit into single sms message
    if len(msg) > SMS_MSG_LIMIT and not args.no_truncate:
        msg = msg[:(SMS_MSG_LIMIT-3)] + "..."

    error = ""

    # split up message into multiple api calls due to api limit
    if len(msg) > API_MSG_LIMIT:
        for i in range(len(msg) // API_MSG_LIMIT):
            offset = i*API_MSG_LIMIT
            partial_msg = msg[offset:(offset+API_MSG_LIMIT)]
            partial_error = post(args.key, args.phone, partial_msg)

            if len(partial_error) > 0:
                error += partial_error + "\n"
    else:
        error = post(args.key, args.phone, msg)

    if len(error) > 0:
        print(error, file=sys.stderr)
        # append failed message to file for later retry
        if args.filename:
            with open(args.filename, "a") as file:
                file.write(msg)
        else:
            print(msg)

        exit(1)
    return


main()
