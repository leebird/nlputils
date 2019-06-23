#!/usr/bin/env bash

VERSION=$1
STANFORD_PORT=$2
BLLIP_PORT=$3

echo "Stanford CoreNLP version: " $VERSION
echo "Stanford CoreNLP port: " $STANFORD_PORT
echo "BLLIP port: " $BLLIP_PORT

CLASSPATH_PREFIX=lib/stanford-corenlp-${VERSION}-models.jar \
target/appassembler/bin/nlpserver ${STANFORD_PORT} 20 300 localhost ${BLLIP_PORT}
