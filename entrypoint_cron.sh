#!/bin/sh

# Start cron in the background
cron

# Tail the cron log to keep the container running
tail -f /var/log/cron.log
