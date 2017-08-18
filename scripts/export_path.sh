#!/usr/bin/env bash

# Get path information.
source "$(dirname ${BASH_SOURCE})"/common_path.sh

# Compile-time C headers path.
CPATH=${DEPENDENCY_PATH}/grpc/include:${DEPENDENCY_PATH}/protobuf/src:$CPATH
export CPATH

# Link-time library path.
LIBRARY_PATH=${DEPENDENCY_PATH}/protobuf/src/.libs:${DEPENDENCY_PATH}/grpc/libs/opt:$LIBRARY_PATH
export LIBRARY_PATH

# Binary command path.
PATH=${DEPENDENCY_PATH}/protobuf/src:${DEPENDENCY_PATH}/grpc/bins/opt:${DEPENDENCY_PATH}/apache-maven/bin:$PATH
export PATH

# Run-time library path.
LD_LIBRARY_PATH=${DEPENDENCY_PATH}/protobuf/src/.libs:${DEPENDENCY_PATH}/grpc/libs/opt:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH

# Use cpp backend for python protocol buffer to make it much faster.
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
