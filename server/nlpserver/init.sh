#!/usr/bin/env bash

set -e

# Compile java codes using Maven and generate command line.
mvn compile
mvn package
mvn package appassembler:assemble

# Download models.
rm -rf lib
mkdir -p lib
wget http://search.maven.org/remotecontent?filepath=edu/stanford/nlp/stanford-corenlp/3.8.0/stanford-corenlp-3.8.0-models.jar \
-O lib/stanford-corenlp-3.8.0-models.jar
