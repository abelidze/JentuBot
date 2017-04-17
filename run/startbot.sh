#!/bin/bash
echo "Starting JentuBot Services..."
sleep 1

screen -S JentuBot -c startbot.conf

sleep 2
echo "JentuBot Started! <-> Type 'screen -r' to attach session"