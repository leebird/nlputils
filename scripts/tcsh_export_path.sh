#!/bin/tcsh
set CWD="`dirname ${PWD}`"

# Compile-time C headers path.
if ( ! ($?CPATH) ) then
    setenv CPATH ${CWD}/dep/grpc/include:${CWD}/dep/protobuf/src
else
    setenv CPATH ${CPATH}:${CWD}/dep/grpc/include:${CWD}/dep/protobuf/src
endif

# Link-time library path.
if ( ! ($?LIBRARY_PATH) ) then
    setenv LIBRARY_PATH ${CWD}/dep/protobuf/src/.libs:${CWD}/dep/grpc/libs/opt
else
    setenv LIBRARY_PATH ${CWD}/dep/protobuf/src/.libs:${CWD}/dep/grpc/libs/opt:$LIBRARY_PATH
endif

# Binary command path.
if ( ! ($?PATH) ) then
    setenv PATH ${CWD}/dep/protobuf/src:${CWD}/dep/grpc/bins/opt
else
    setenv PATH ${CWD}/dep/protobuf/src:${CWD}/dep/grpc/bins/opt:$PATH
endif

# Run-time library path.
if ( ! ($?LD_LIBRARY_PATH) ) then
    setenv LD_LIBRARY_PATH ${CWD}/dep/protobuf/src/.libs:${CWD}/dep/grpc/libs/opt
else
    setenv LD_LIBRARY_PATH ${CWD}/dep/protobuf/src/.libs:${CWD}/dep/grpc/libs/opt:$LD_LIBRARY_PATH
endif

