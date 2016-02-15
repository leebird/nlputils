#!/bin/tcsh

# Compile-time C headers path.
if ( ! ($?CPATH) ) then
    setenv CPATH ${PWD}/dep/grpc/include
else
    setenv CPATH ${CPATH}:${PWD}/dep/grpc/include
endif

# Link-time library path.
if ( ! ($?LIBRARY_PATH) ) then
    setenv LIBRARY_PATH ${PWD}/dep/protobuf/src/.libs:${PWD}/dep/grpc/libs/opt
else
    setenv LIBRARY_PATH ${PWD}/dep/protobuf/src/.libs:${PWD}/dep/grpc/libs/opt:$LIBRARY_PATH
endif

# Binary command path.
if ( ! ($?PATH) ) then
    setenv PATH ${PWD}/dep/protobuf/src:${PWD}/dep/grpc/bins/opt
else
    setenv PATH ${PWD}/dep/protobuf/src:${PWD}/dep/grpc/bins/opt:$PATH
endif

# Run-time library path.
if ( ! ($?LD_LIBRARY_PATH) ) then
    setenv LD_LIBRARY_PATH ${PWD}/dep/protobuf/src/.libs:${PWD}/dep/grpc/libs/opt
else
    setenv LD_LIBRARY_PATH ${PWD}/dep/protobuf/src/.libs:${PWD}/dep/grpc/libs/opt:$LD_LIBRARY_PATH
endif

