#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
echo -en '\n'
echo -e "${RED}**********************************************"
echo    "*** Welcome to the Dewheater Camera installer ***"
echo -e "**********************************************${NC}"
echo -en '\n'

#echo -en "${GREEN}* Dependencies installation\n${NC}"
#pip3 install pyowm adafruit_DHT
#echo -en '\n'


echo -en "${GREEN}* Autostart script\n${NC}"
cp ./dewheater.service /lib/systemd/system/
chown root:root /lib/systemd/system/dewheater.service
chmod 0644 /lib/systemd/system/dewheater.service
echo -en '\n'

echo -en "${GREEN}* Configure log rotation\n${NC}"
cp ./dewheater.logrotate /etc/logrotate.d/dewheater
chown root:root /etc/logrotate.d/dewheater
chmod 0644 /etc/logrotate.d/dewheater
cp ./dewheater_data.logrotate /etc/logrotate.d/dewheater_data
chown root:root /etc/logrotate.d/dewheater_data
chmod 0644 /etc/logrotate.d/dewheater_data
cp ./dewheater.conf /etc/rsyslog.d/ 
chown root:root /etc/rsyslog.d/dewheater.conf
chmod 0644 /etc/rsyslog.d/dewheater.conf
echo -en '\n'

echo -en "${GREEN}* Copy dewheater configuration file\n${NC}"
cp settings_dewheater.json.repo settings_dewheater.json
test -d /etc/raspap && cp  settings_dewheater.json /etc/raspap/

chown -R `logname`:`logname` dewheater.py
systemctl daemon-reload
#systemctl enable dewheater.service
echo -en '\n'

