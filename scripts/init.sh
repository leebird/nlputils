#!/usr/bin/env bash

# Stop if error occurs.
set -e

# Get path information.
source "$(dirname $BASH_SOURCE)"/common_path.sh

# Version numbers of the dependency libraries.
# Check https://github.com/google/protobuf/releases for correct tag.
PROTOBUF_VERSION="v3.0.0"
# Check https://github.com/grpc/grpc/releases for correct tag.
GRPC_VERSION="v1.0.0"
# Check https://github.com/grpc/grpc-java/releases for correct tag.
GRPC_JAVA_VERSION="v1.0.0"

# Download packages from Github.
# https://github.com/google/protobuf/releases
cd ${DEPENDENCY_PATH}
git clone https://github.com/google/protobuf
cd protobuf
git checkout tags/${PROTOBUF_VERSION}

# The C++ based grpc stack, including python and other languages.
# https://github.com/grpc/grpc
cd ${DEPENDENCY_PATH}
git clone https://github.com/grpc/grpc
cd grpc
git checkout tags/${GRPC_VERSION}
git submodule update --init

# Java grpc library.
cd ${DEPENDENCY_PATH}
git clone https://github.com/grpc/grpc-java
cd grpc-java
git checkout tags/${GRPC_JAVA_VERSION}

# Make protobuf.
# Generate configuration files
cd ${DEPENDENCY_PATH}/protobuf

# Check that gmock is present. Usually it is already there since the directory
# is set up as an SVN external. This is copied from the master branch of
# protocol buffer as it's not released yet.
if test ! -e gmock; then
  echo "Google Mock not present.  Fetching gmock-1.7.0 from the web..."
  curl -L -O https://github.com/google/googlemock/archive/release-1.7.0.zip
  unzip -q release-1.7.0.zip
  rm release-1.7.0.zip
  mv googlemock-release-1.7.0 gmock

  curl -L -O https://github.com/google/googletest/archive/release-1.7.0.zip
  unzip -q release-1.7.0.zip
  rm release-1.7.0.zip
  mv googletest-release-1.7.0 gmock/gtest
fi

./autogen.sh
./configure
make
make check

# Make the java protobuf package.
cd java
mvn test
mvn package

# Make grpc.
cd ${DEPENDENCY_PATH}/grpc
make

# Install Python modules. First update pip.
pip install -U pip

# Protobuf Python module.
# Use the C++ backend for serialization. Pure
# python serialization is very slow.
# export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
# before running your python application to use
# the C++ backend.
cd ${DEPENDENCY_PATH}/protobuf/python
python setup.py build --cpp_implementation
python setup.py test --cpp_implementation
python setup.py install --cpp_implementation

# Grpc python library.
# We don't install from the codes since it lacks setup.py.
# Some instructions: https://github.com/grpc/grpc/blob/master/INSTALL
# Not very clear.
cd ${ROOT_PATH}
pip install grpcio

# Grpc java library compiler.
# Here we only build the compiler, the libarary jar file can be downloaded
# from maven as other dependencies.
cd ${DEPENDENCY_PATH}/grpc-java/compiler
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
pip install git+https://github.com/leebird/glog
