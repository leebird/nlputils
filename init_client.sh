#!/usr/bin/env bash

# Initialization for a python client.
CWD=$PWD
echo $CWD
mkdir dep

# Download packages from Github.
# https://github.com/google/protobuf/releases
cd ${CWD}/dep
rm -rf protobuf
git clone https://github.com/google/protobuf
cd protobuf
git checkout tags/v3.0.0-beta-1

# The C++ based grpc stack, including python and other languages.
# https://github.com/grpc/grpc
cd ${CWD}/dep
rm -rf grpc
git clone https://github.com/grpc/grpc.git
cd grpc
git checkout tags/release-0_12_0
git submodule update --init

# Make packages.
# Make protobuf.
# Generate configuration files
cd ${CWD}/dep/protobuf
./autogen.sh
./configure
make
make check
# sudo make install
# To delete the system-level installation
# make uninstall

# Make grpc.
cd ${CWD}/dep/grpc
make
#sudo make install

# Install Python modules.
# Protobuf Python module.
cd ${CWD}/dep/protobuf/python
python setup.py install

# Grpc python library.
pip install grpcio
