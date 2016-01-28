#!/usr/bin/env bash


# https://github.com/google/protobuf/releases

git clone https://github.com/google/protobuf
cd protobuf
git checkout tags/v3.0.0-beta-1

# Generate configuration files
./autogen.sh
./configure
make
make check
make install

# To delete the system installation
# make uninstall

# Install python dependencies.
cd python
python setup.py install

# Install java dependencies.
cd java
mvn test
# Build a jar file.
mvn package

# The C++ based grpc stack, including python and other languages.
# https://github.com/grpc/grpc
git clone https://github.com/grpc/grpc.git
cd grpc
git checkout tags/release-0_11_1
git submodule update --init
make
sudo make install

# Install grpc python library.
# Use build_python.sh to build the Python code and install it into a virtual environment
# Look into tools/run_tests/build_python.sh for commands, or, just use pip as following.
# Interestingly gRPC doesn't suppory python3.4 until post-beta.
# Use python 2.7 with python 3 compatible codes.
pip install grpcio

# The java rpc stack
# https://github.com/grpc/grpc-java
# git clone https://github.com/grpc/grpc-java
# cd grpc-java
# git checkout tags/v0.9.0
# To build, https://github.com/grpc/grpc-java/blob/master/COMPILING.md

# The plugin binds the rpc stack with protobuf
# https://github.com/grpc/grpc-java/tree/master/compiler
# Change to the compiler directory:
cd compiler
# To compile the plugin:
../gradlew java_pluginExecutable
# To test the plugin with the compiler:
../gradlew test

# Also need to download 3 dependencies, Guava, Netty and hpack for gRPC
# https://github.com/google/guava/
# Note that only netty>=4.1 has the required APIs. Now we use netty-4.1.0.Beta6
# http://netty.io/
# Also need to download hpack
#git clone https://github.com/twitter/hpack.git
#mvn test
# mvn package

