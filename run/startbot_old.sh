#!/bin/bash
echo "Starting JentuBot Services..."

cd ../config
screen -U -dmS "Redis" redis-server redis.conf
echo "Redis started!"
sleep 3

cd ..
export C_FORCE_ROOT='true'
screen -U -dmS "Celery" celery worker -A tasks --loglevel=info
echo "Celery started!"
sleep 3

screen -U -dmS "JentuBot" ./loopbot.sh
echo "JentuBot started!"
sleep 2

cd jentudb
echo "JentuPHP started!"
sleep 1
screen -t JentuPHP sudo php -S 0.0.0.0:80