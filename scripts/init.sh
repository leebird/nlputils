#!/usr/bin/env bash

# Initialization for a python client.
set -e

# Set version tags. Please check the corresponding git repo
# for correct tags.
PROTOBUF_VERSION="v3.0.0-beta-3"
# 02/12/2016 Currently grpc has compile error using protobuf v3 beta 2.
GRPC_VERSION="release-0_15_0"
GRPC_JAVA_VERSION="v0.15.0"

# Set folder.
SCRIPT_CWD=$PWD
CWD="$(dirname ${SCRIPT_CWD})"
echo $CWD
rm -rf $CWD/dep
mkdir -p $CWD/dep

# Download packages from Github.
# https://github.com/google/protobuf/releases
cd ${CWD}/dep
git clone https://github.com/google/protobuf
cd protobuf
git checkout tags/${PROTOBUF_VERSION}

# The C++ based grpc stack, including python and other languages.
# https://github.com/grpc/grpc
cd ${CWD}/dep
git clone https://github.com/grpc/grpc
cd grpc
git checkout tags/${GRPC_VERSION}
git submodule update --init

# Java grpc library.
cd ${CWD}/dep
git clone https://github.com/grpc/grpc-java
cd grpc-java
git checkout tags/${GRPC_JAVA_VERSION}

# Make protobuf.
# Generate configuration files
cd ${CWD}/dep/protobuf
./autogen.sh
./configure
make
make check

cd java
mvn test
mvn package
# sudo make install
# To delete the system-level installation
# make uninstall

# Make grpc.
cd ${CWD}/dep/grpc
make
#sudo make install

# Install Python modules.
# Update pip.
pip install -U pip

# Protobuf Python module.
# Use the C++ backend for serialization. Pure
# python serialization is very slow.
# export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
# before running your python application to use
# the C++ backend.
cd ${CWD}/dep/protobuf/python
python setup.py build --cpp_implementation
python setup.py test --cpp_implementation
python setup.py install --cpp_implementation

# Grpc python library.
# We don't install from the codes since it lacks setup.py.
# Some instructions: https://github.com/grpc/grpc/blob/master/INSTALL
# Not very clear.
cd ${CWD}
pip install grpcio

# Grpc java library compiler.
# Here we only build the compiler, the libarary jar file can be downloaded
# from maven as other dependencies.
cd ${CWD}/dep/grpc-java/compiler
# To build, https://github.com/grpc/grpc-java/blob/master/COMPILING.md
# The plugin binds the rpc stack with protobuf
# https://github.com/grpc/grpc-java/tree/master/compiler
# Change to the compiler directory:
# To compile the plugin:
../gradlew java_pluginExecutable
# To test the plugin with the compiler:
../gradlew test

# Other Python modules.
pip install -U shortuuid
pip install -U bllipparser
