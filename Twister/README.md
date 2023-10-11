# Installation
```
sudo apt-get install autoconf automake bison flex g++ libavahi-client-dev libcppunit-dev libftdi-dev liblo-dev libmicrohttpd-dev libncurses-dev libprotobuf-dev libprotoc-dev libtool libusb-1.0.0-dev make protobuf-compiler pkg-config uuid-dev zlib1g-dev
```
```
sudo apt-get install python3-numpy python3-protobuf
```
```
git clone https://github.com/OpenLightingProject/ola.git
```
cd ola 
autoreconf -i
./configure --enable-python-libs --prefix=/usr
make -j4 
sudo make install 
```