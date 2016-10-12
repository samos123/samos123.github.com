#!/bin/python3
import sys
import datetime
import parse_speed
import publish_bandwidth


def get_yesterday_log(dir="/var/log/", prefix="speed-check-"):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    return dir + prefix + yesterday.isoformat(), yesterday


if __name__ == "__main__":
    filename, date = get_yesterday_log()
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        date = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d").date()

    results = parse_speed.parse(filename)
    publish_bandwidth.publish(results, date)
