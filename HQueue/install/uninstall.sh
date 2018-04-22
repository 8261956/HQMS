#!/bin/sh

InstallDir="/usr/local/clearcrane/hqms/bin"
SERVICE_NAME=hqms_sync

/etc/init.d/$SERVICE_NAME stop
sleep 1

rm -rf $InstallDir
rm -rf $DataDir 

#update-rc.d -f $SERVICE_NAME remove


rm /etc/rc2.d/S50$SERVICE_NAME
rm /etc/rc3.d/S50$SERVICE_NAME
rm /etc/rc4.d/S50$SERVICE_NAME
rm /etc/rc5.d/S50$SERVICE_NAME

rm /etc/init.d/$SERVICE_NAME
