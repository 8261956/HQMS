#!/bin/bash

while :;
do
	python /home/clear/hqueue/backend/sync.py $*
	sleep 5
done
