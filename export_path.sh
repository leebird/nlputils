# Compile-time C headers path.
CPATH=${PWD}/dep/grpc/include:$CPATH
export CPATH

# Link-time library path.
LIBRARY_PATH=${PWD}/dep/protobuf/src/.libs:${PWD}/dep/grpc/libs/opt:$LIBRARY_PATH
export LIBRARY_PATH

# Binary command path.
PATH=${PWD}/dep/protobuf/src:${PWD}/dep/grpc/bins/opt:$PATH
export PATH

# Run-time library path.
LD_LIBRARY_PATH=${PWD}/dep/protobuf/src/.libs:${PWD}/dep/grpc/libs/opt:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH
