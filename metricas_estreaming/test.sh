#!/bin/bash

tcpdump -i $3 port 80 or port 443 -w test.pcap &
TCPDUMP_PID=$!


nohup bash ./execute_streaming.sh $1 $2 & 
STREAM_PID=$!


sleep 60
kill $STREAM_PID $TCPDUMP_PID

pkill -9 -f streamlink
