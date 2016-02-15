#!/bin/sh
# Don't use stanford-corenlp-full-2015-04-20/* as there is a protobuf.jar under Stanford CoreNLP folder!!!
CLASSPATH="lib/stanford-corenlp-3.6.0.jar\
:lib/stanford-corenlp-3.6.0-models.jar\
:lib/protobuf-java-3.0.0-beta-1.jar\
:lib/grpc-all-0.12.0.jar\
:lib/netty-all-4.1.0.Beta6.jar\
:lib/guava-19.0.jar\
:lib/hpack-1.0.1.jar\
:../protolib/java/"

javac -classpath ${CLASSPATH} -d bin/ src/StanfordTest.java

CLASSPATH="lib/stanford-corenlp-3.6.0.jar\
:lib/stanford-corenlp-3.6.0-models.jar\
:lib/slf4j-api.jar\
:lib/protobuf-java-3.0.0-beta-1.jar\
:lib/grpc-all-0.12.0.jar\
:lib/netty-all-4.1.0.Beta6.jar\
:lib/guava-19.0.jar\
:lib/hpack-1.0.1.jar\
:../protolib/java/:bin"

java -classpath ${CLASSPATH} StanfordTest

