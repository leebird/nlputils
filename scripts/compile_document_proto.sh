#!/usr/bin/env bash

set -e

# Get path information.
source "$(dirname $BASH_SOURCE)"/common_path.sh

# Create folders.
rm -rf ${ROOT_PATH}/protolib/python
rm -rf ${ROOT_PATH}/protolib/java
mkdir -p ${ROOT_PATH}/protolib/python
mkdir -p ${ROOT_PATH}/protolib/java
touch ${ROOT_PATH}/protolib/python/__init__.py
touch ${ROOT_PATH}/protolib/__init__.py

# Compile python codes.
protoc --proto_path=${ROOT_PATH}/proto --python_out=${ROOT_PATH}/protolib/python \
--grpc_out=${ROOT_PATH}/protolib/python --plugin=protoc-gen-grpc=`which grpc_python_plugin` \
${ROOT_PATH}/proto/document.proto

# Compile java codes.
protoc --plugin=protoc-gen-grpc-java=${DEPENDENCY_PATH}/grpc-java/compiler/build/exe/java_plugin/protoc-gen-grpc-java \
--proto_path=${ROOT_PATH}/proto --grpc-java_out=${ROOT_PATH}/protolib/java \
--java_out=${ROOT_PATH}/protolib/java ${ROOT_PATH}/proto/document.proto
javac -classpath "${DEPENDENCY_PATH}/protobuf/java/core/target/protobuf-java-3.4.1.jar" \
${ROOT_PATH}/protolib/java/edu/delaware/nlp/DocumentProto.java

###EDG Rules Proto
# Compile python codes.
protoc --proto_path=${ROOT_PATH}/proto --python_out=${ROOT_PATH}/protolib/python \
--grpc_out=${ROOT_PATH}/protolib/python --plugin=protoc-gen-grpc=`which grpc_python_plugin` \
${ROOT_PATH}/proto/edgRules.proto

# Compile java codes.
protoc --plugin=protoc-gen-grpc-java=${DEPENDENCY_PATH}/grpc-java/compiler/build/exe/java_plugin/protoc-gen-grpc-java \
--proto_path=${ROOT_PATH}/proto --grpc-java_out=${ROOT_PATH}/protolib/java --java_out=${ROOT_PATH}/protolib/java \
${ROOT_PATH}/proto/edgRules.proto
javac -classpath "${DEPENDENCY_PATH}/protobuf/java/core/target/protobuf-java-3.4.1.jar" \
${ROOT_PATH}/protolib/java/edu/delaware/nlp/EdgRulesProto.java

# Compile rpc proto.
# Compile python codes.
protoc --proto_path=${ROOT_PATH}/proto --python_out=${ROOT_PATH}/protolib/python \
--grpc_out=${ROOT_PATH}/protolib/python --plugin=protoc-gen-grpc=`which grpc_python_plugin` \
${ROOT_PATH}/proto/rpc.proto

# Compile java codes.
protoc --plugin=protoc-gen-grpc-java=${DEPENDENCY_PATH}/grpc-java/compiler/build/exe/java_plugin/protoc-gen-grpc-java \
--proto_path=${ROOT_PATH}/proto --grpc-java_out=${ROOT_PATH}/protolib/java --java_out=${ROOT_PATH}/protolib/java \
${ROOT_PATH}/proto/rpc.proto
javac -classpath "${DEPENDENCY_PATH}/protobuf/java/core/target/protobuf-java-3.4.1.jar:${ROOT_PATH}/protolib/java" \
${ROOT_PATH}/protolib/java/edu/delaware/nlp/RpcProto.java
