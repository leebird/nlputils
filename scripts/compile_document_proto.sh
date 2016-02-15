#!/usr/bin/env bash
protoc --proto_path=../proto --python_out=../protolib/python --grpc_out=../protolib/python --plugin=protoc-gen-grpc=`which grpc_python_plugin` ../proto/document.proto

protoc --plugin=protoc-gen-grpc-java=../dep/grpc-java/compiler/build/binaries/java_pluginExecutable/protoc-gen-grpc-java \
--proto_path=../proto --grpc-java_out=../protolib/java --java_out=../protolib/java ../proto/document.proto

javac -classpath "../dep/protobuf/java/target/protobuf-java-3.0.0-beta-1.jar" ../protolib/java/edu/delaware/nlp/Protobuf.java
