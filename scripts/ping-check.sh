#!/bin/sh

today=$(date +"%Y-%m-%d")
time=$(date -I'seconds')
echo "Pinging 8.8.8.8 at $time" >> /var/log/ping-check-$today
ping -c 5 8.8.8.8 | grep -E "round-trip|packet loss" >> /var/log/ping-check-$today
