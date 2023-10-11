# Installation
## ola
go to `/home/pi`
```
sudo apt-get install autoconf automake bison flex g++ libavahi-client-dev libcppunit-dev libftdi-dev liblo-dev libmicrohttpd-dev libncurses-dev libprotobuf-dev libprotoc-dev libtool libusb-1.0.0-dev make protobuf-compiler pkg-config uuid-dev zlib1g-dev
```
```
sudo apt-get install python3-numpy python3-protobuf
```
```
git clone https://github.com/OpenLightingProject/ola.git
```
```
cd ola 
autoreconf -i
./configure --enable-python-libs --prefix=/usr
make -j4 
sudo make install 
```
```
sudo adduser olad tty
```
```
sudo systemctl disable serial-getty@ttyAMA0.service
```
then open `/boot/config.txt` (with nano for instance) and add the lines (somewhere in the file) and close the file with ctrl+o, enter, ctrl+x
```
dtoverlay=disable-bt
enable_uart=1
init_uart_clock=16000000
```
then open `/home/midirasp2/.ola/ola-uartdmx.conf` (with nano for instance) and fill it with
```
/dev/ttyAMA0-break = 100
/dev/ttyAMA0-malf = 24000
device = /dev/ttyAMA0
enabled = true
```
then run `sudo nano /usr/bin/set_dmx_mode` and copy paste:
```
#!/bin/sh
# set_dmx_mode
pin=18
gpio=/sys/class/gpio/gpio$pin
if [ $# -lt 1 ] ; then 
  echo "$0 : on or off?"
  exit 1
fi

if [ ! -d $gpio ] ; then 
   echo $pin > /sys/class/gpio/export
fi
echo out > $gpio/direction
echo $1 > $gpio/value
```
then open the file `/etc/rc.local` and add the following lines before the `exit 0` line:
```
chmod 777 /dev/ttyAMA0
sudo /usr/bin/set_dmx_mode 1
/usr/bin/olad -l 3
```
## Twister
### Python stuff
```
sudo apt install -y python3-pip libsdl2-2.0-0 libsdl2-mixer-2.0-0
pip install pygame
pip install RPiMCP23S17
```
Change user name in first lines of code in the sys.path.append(/home/.../ola/python)

### Twister repo
go to `/home/pi`
```
git clone https://github.com/PaoloRondot/TwisterSimon.git
```
```
cd TwisterSimon
git checkout dmx
```
