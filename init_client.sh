#!/usr/bin/env bash

# Initialization for a python client.
CWD=$PWD
echo $CWD
mkdir dep

# Install protobuf dependencies.
# https://github.com/google/protobuf/releases
cd ${CWD}/dep
rm -rf protobuf
git clone https://github.com/google/protobuf
cd protobuf
git checkout tags/v3.0.0-beta-2

# Generate configuration files
./autogen.sh
./configure
make
make check
sudo make install

# To delete the system-level installation
# make uninstall

# Install python dependencies.
cd python
python setup.py install


# Install grpc dependencies.
# The C++ based grpc stack, including python and other languages.
# https://github.com/grpc/grpc
cd ${CWD}/dep
rm -rf grpc
git clone https://github.com/grpc/grpc.git
cd grpc
git checkout tags/release-0_12_0
git submodule update --init
make
sudo make install

# Install grpc python library.
pip install grpcio
