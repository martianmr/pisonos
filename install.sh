#!/bin/bash

# install.sh
#
# bash script to remotely install pisonos on Rasberry Pi
# Usage: install.sh [-qu] ip_address [user]
# -q quick install, skips all steps except copying the files to the Pi
# -u update install, skips steps only required on first setup
# default is to perform all steps needed on first setup

set -e

print_usage() {
  printf "Usage: install.sh [-qu] ip_address [user]\n"
}

mode=install

while getopts 'qu' flag; do
  case "${flag}" in
    q) mode=quick ;;
    u) mode=update ;;
    *) print_usage
       exit 2 ;;
  esac
done
shift $((OPTIND-1))

if [ $# -lt "1" ]
then
  print_usage
  exit 2
fi

USER=${2:-pi}
IP=$1
rawgpio=no # rawgpio only needed for legacy build (without Adafruit LCD)
player=UNDEFINED
if [ ! -f $IP.cfg ]
then
  echo File \'$IP.cfg\' not found, please create this file and add e.g. player=\'My Sonos Room Name\'
  exit 1
fi
source $IP.cfg
cp pisonos.cfg.base pisonos/pisonos.cfg
sed -r -i'' -e "s#(player .*=.)[^\s]*#\1${player}#" -e "s#(rawgpio .*=.)[^\s]*#\1${rawgpio}#" ./pisonos/pisonos.cfg
tar cvfz pisonos.tar.gz pisonos
scp pisonos.tar.gz $USER@$IP:/home/$USER/
ssh $USER@$IP tar xvfz pisonos.tar.gz
ssh $USER@$IP rm pisonos.tar.gz
if [ "$mode" == "quick" ]
then
  ssh $USER@$IP sudo systemctl restart pisonos
elif [ "$mode" == "update" ]
then
  ssh $USER@$IP /home/$USER/pisonos/setup.sh -u
else
  ssh $USER@$IP /home/$USER/pisonos/setup.sh
fi
rm pisonos/pisonos.cfg
rm pisonos.tar.gz
