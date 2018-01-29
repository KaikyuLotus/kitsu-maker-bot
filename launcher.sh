#!/bin/bash

echo "Starting..."
while :
do
 pkill -f MainKitsu.py
 python3 MainKitsu.py
 sleep 5
 echo "Restarting..."
done