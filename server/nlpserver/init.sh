#!/usr/bin/env bash

set -e

if [ -n "$1" ]; then
    VERSION=$1
else
    VERSION="3.6.0"
fi

echo "Stanford CoreNLP version: " $VERSION

# Compile java codes using Maven and generate command line.
mvn clean
mvn -Dnlpversion=$VERSION compile package
mvn package appassembler:assemble

# Download models.
rm -rf lib
mkdir -p lib
wget http://search.maven.org/remotecontent?filepath=edu/stanford/nlp/stanford-corenlp/${VERSION}/stanford-corenlp-${VERSION}-models.jar \
-O lib/stanford-corenlp-${VERSION}-models.jar
