#!/bin/bash


# Check if Redis is already running
if pgrep -x "redis-server" > /dev/null
then
    echo "Redis is already running."
else
    # Start Redis with the specified configuration file
    redis-server $REDIS_CONFIG
    echo "Redis has been started."
fi