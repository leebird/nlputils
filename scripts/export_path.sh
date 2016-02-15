# Set folder.
SCRIPT_CWD=$PWD
CWD="$(dirname ${SCRIPT_CWD})"

# Compile-time C headers path.
CPATH=${CWD}/dep/grpc/include:${CWD}/dep/protobuf/src:$CPATH
export CPATH

# Link-time library path.
LIBRARY_PATH=${CWD}/dep/protobuf/src/.libs:${CWD}/dep/grpc/libs/opt:$LIBRARY_PATH
export LIBRARY_PATH

# Binary command path.
PATH=${CWD}/dep/protobuf/src:${CWD}/dep/grpc/bins/opt:$PATH
export PATH

# Run-time library path.
LD_LIBRARY_PATH=${CWD}/dep/protobuf/src/.libs:${CWD}/dep/grpc/libs/opt:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH
