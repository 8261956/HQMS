#!/usr/bin/env bash

while :;
do
    pyfile=./wx_sync.py
	count=`ps -ef |grep $pyfile |grep -v "grep" |wc -l`
    if [ 0 == $count ];then
        python $pyfile
    fi
	sleep 5
done