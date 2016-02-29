#!/usr/bin/env bash

mkdir -p bin

# Don't use stanford-corenlp-full-2015-04-20/* as there is a protobuf.jar under Stanford CoreNLP folder!!!
CLASSPATH="lib/stanford-corenlp-3.6.0.jar\
:lib/stanford-corenlp-3.6.0-models.jar\
:lib/protobuf-java-3.0.0-beta-1.jar\
:lib/grpc-all-0.12.0.jar\
:lib/netty-all-4.1.0.Beta8.jar\
:lib/guava-19.0.jar\
:lib/hpack-v1.0.1.jar\
:../../protolib/java/:./src/"

javac -classpath ${CLASSPATH} -d bin/ src/BllipUtil.java src/StanfordUtil.java src/NlpServer.java

CLASSPATH="lib/stanford-corenlp-3.6.0.jar\
:lib/stanford-corenlp-3.6.0-models.jar\
:lib/slf4j-api.jar\
:lib/protobuf-java-3.0.0-beta-1.jar\
:lib/grpc-all-0.12.0.jar\
:lib/netty-all-4.1.0.Beta8.jar\
:lib/guava-19.0.jar\
:lib/hpack-v1.0.1.jar\
:lib/okhttp-2.5.0.jar\
:lib/okio-1.6.0.jar\
:../../protolib/java/:bin"

# Listening port, threads, time-out, Bllip server & port.
java -classpath ${CLASSPATH} NlpServer 8900 20 300 localhost 8901

