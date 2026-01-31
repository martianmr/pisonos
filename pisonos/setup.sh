#!/bin/bash

# setup.sh
#
# bash script to setup pisonos
# Usage: setup.sh [-u]
# -u update install, skips steps only required on first setup
# default is to perform all steps needed on first setup

set -e

print_usage() {
  printf "Usage: setup.sh [-u]\n"
}

update=false

while getopts 'u' flag; do
  case "${flag}" in
    u) update=true ;; # set this option to skip things we only do on first install
    *) print_usage
       exit 2 ;;
  esac
done
shift $((OPTIND-1))

echo "=== STARTING PISONOS INSTALL ==="
date
# Stop the pisonos service and enter the app directory
systemctl status pisonos && sudo systemctl stop pisonos || true
cd $(dirname $0)
pwd
HOMEDIR=$(pwd)
USER=$(whoami)
# Fixup file permissions
find . -maxdepth 1 -type f -exec chmod 644 {} \;
chmod +x setup.sh
echo "=== CONFIGURING FIRMWARE ==="
# Add i2c support for Adafruit
sudo raspi-config nonint do_i2c 0
# Increase i2c baud rate to 400kHz for better display response
sudo sed -i -e 's/^dtparam=i2c_arm=on.*$/dtparam=i2c_arm=on,i2c_arm_baudrate=400000/' /boot/firmware/config.txt
# Add lirc suport on GPIO pin 18
grep gpio-ir /boot/firmware/config.txt || (echo 'dtoverlay=gpio-ir,gpio_pin=18' | sudo tee -a /boot/firmware/config.txt)
if [ "$update" == "false" ]
then
  echo "=== INSTALLING PACKAGES ==="
  sudo apt-get -y update
  sudo apt-get -y install python3-lxml
  sudo apt-get -y install lirc
  sudo apt-get -y install python3-dev
  sudo apt-get -y install libxslt1-dev
  sudo apt-get -y install liblirc-dev
fi
echo "=== SETTING UP LIRC ==="
# Update the LIRC config files and restart lircd
sudo sed -r -i'' -e 's#(driver .*=.)[^\s]*#\1default#' -e 's#(device .*=.)[^\s]*#\1/dev/lirc0#' /etc/lirc/lirc_options.conf
sudo cp lirc/lircrc /etc/lirc/
sudo cp lirc/*.lircd.conf /etc/lirc/lircd.conf.d/
sudo systemctl restart lircd
systemctl status lircd || true
echo "=== SETTING UP PYTHON ==="
# Create and activate the venv we're going to use for pisonos
[ -d venv ] || python -m venv venv
. venv/bin/activate
# Install system lirc support in local venv
lircversion=$(apt show lirc | grep Version | cut -d' ' -f'2' | cut -d'-' -f1)
if ! pip list --format freeze | grep "lirc==$lircversion"
then
  tar xvfz /usr/share/lirc/lirc-${lircversion}.tar.gz
  sed -i'' -e "s#LIRCVERSION#$lircversion#g" lirc/lirc_pyproject.toml
  mv lirc/lirc_pyproject.toml lirc-${lircversion}/pyproject.toml
  pip install ./lirc-${lircversion}
fi
rm -rf ./lirc-${lircversion}
# Install other dependencies
pip install -r requirements.txt
deactivate
echo "=== SETTING UP SERVICE ==="
# Set up pisonos to start in venv using systemd
sed -i'' -e "s#HOMEDIR#$HOMEDIR#g" pisonos.service
sed -i'' -e "s#USER#$USER#g" pisonos.service
sudo cp pisonos.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pisonos
systemctl status pisonos || true
if [ "$update" == "false" ]
then
  echo "=== REBOOTING ==="
  date
  sleep 1
  sudo reboot now
else
  echo "=== STARTING PISONS ==="
  sudo systemctl stop lircd
  sudo systemctl restart lircd.socket
  sudo systemctl start lircd
  sudo systemctl start pisonos
  systemctl status pisonos 
fi
