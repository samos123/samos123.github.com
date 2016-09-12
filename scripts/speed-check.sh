#!/bin/sh

today=$(date +"%Y-%m-%d")
time=$(date -I'seconds')
sh /root/betterspeedtest.sh --time 20 >> /var/log/speed-check-$today
echo "" >> /var/log/speed-check-$today
