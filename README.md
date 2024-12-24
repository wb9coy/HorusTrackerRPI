# HorusTrackerRPI
Uses an RFM9x chip to transmit 4FSK Horus on a RPI zero

sudo apt install cmake
sudo pip install horusdemodlib --break-system-packages

git clone https://github.com/projecthorus/horusdemodlib.git
cd horusdemodlib && mkdir build && cd build
cmake ..
make
sudo make install
