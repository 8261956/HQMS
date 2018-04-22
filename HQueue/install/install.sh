#!/bin/sh


InstallDir="/usr/local/clearcrane/hqms/bin"
ServiceName=hqms_sync
DemonName=hqms_sync_daemon
LogName=hqmsLog

echo "install into $InstallDir..."

mkdir -p $InstallDir
mkdir -p /var/log/hqms

cp $ServiceName /etc/init.d/$ServiceName
cp $DemonName $InstallDir/
cp uninstall.sh $InstallDir/
cp -f $LogName /etc/logrotate.d/$LogName

ln -s /etc/init.d/$ServiceName /etc/rc2.d/S50$ServiceName
ln -s /etc/init.d/$ServiceName /etc/rc3.d/S50$ServiceName
ln -s /etc/init.d/$ServiceName /etc/rc4.d/S50$ServiceName
ln -s /etc/init.d/$ServiceName /etc/rc5.d/S50$ServiceName

/etc/init.d/$ServiceName start





