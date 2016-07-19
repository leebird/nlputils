#!/usr/bin/env bash
set -e

# Create folders.
rm -rf ../protolib/python
rm -rf ../protolib/java
mkdir -p ../protolib/python
mkdir -p ../protolib/java
touch ../protolib/python/__init__.py
touch ../protolib/__init__.py

# Compile python codes.
protoc --proto_path=../proto --python_out=../protolib/python --grpc_out=../protolib/python --plugin=protoc-gen-grpc=`which grpc_python_plugin` ../proto/document.proto

# Compile java codes.
protoc --plugin=protoc-gen-grpc-java=../dep/grpc-java/compiler/build/exe/java_plugin/protoc-gen-grpc-java \
--proto_path=../proto --grpc-java_out=../protolib/java --java_out=../protolib/java ../proto/document.proto
javac -classpath "../dep/protobuf/java/core/target/protobuf-java-3.0.0-beta-3.jar" ../protolib/java/edu/delaware/nlp/DocumentProto.java

###EDG Rules Proto
# Compile python codes.
protoc --proto_path=../proto --python_out=../protolib/python --grpc_out=../protolib/python --plugin=protoc-gen-grpc=`which grpc_python_plugin` ../proto/edgRules.proto

# Compile java codes.
protoc --plugin=protoc-gen-grpc-java=../dep/grpc-java/compiler/build/exe/java_plugin/protoc-gen-grpc-java \
--proto_path=../proto --grpc-java_out=../protolib/java --java_out=../protolib/java ../proto/edgRules.proto
javac -classpath "../dep/protobuf/java/core/target/protobuf-java-3.0.0-beta-3.jar" ../protolib/java/edu/delaware/nlp/EdgRulesProto.java

# Compile rpc proto.
# Compile python codes.
protoc --proto_path=../proto --python_out=../protolib/python --grpc_out=../protolib/python --plugin=protoc-gen-grpc=`which grpc_python_plugin` ../proto/rpc.proto

# Compile java codes.
protoc --plugin=protoc-gen-grpc-java=../dep/grpc-java/compiler/build/exe/java_plugin/protoc-gen-grpc-java \
--proto_path=../proto --grpc-java_out=../protolib/java --java_out=../protolib/java ../proto/rpc.proto
javac -classpath "../dep/protobuf/java/core/target/protobuf-java-3.0.0-beta-3.jar:../protolib/java/" ../protolib/java/edu/delaware/nlp/RpcProto.java
