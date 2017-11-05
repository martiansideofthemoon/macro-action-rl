Macro Actions for RL
====================

````
git clone https://github.com/LARG/HFO
cd HFO
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=RelwithDebInfo ..
make -j4
make install
cd ../..
make
````

If there is an error with rcssserver, go to https://github.com/mhauskn/rcssserver and install using

````
./configure --with-boost-libdir=/usr/lib/x86_64-linux-gnu
make
sudo make install
````