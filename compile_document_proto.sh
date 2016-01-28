#!/usr/bin/env bash
protoc --proto_path=proto --python_out=protolib/python --grpc_out=protolib/python --plugin=protoc-gen-grpc=`which grpc_python_plugin` proto/document.proto
