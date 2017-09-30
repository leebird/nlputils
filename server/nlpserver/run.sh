#!/usr/bin/env bash

CLASSPATH_PREFIX=lib/stanford-corenlp-3.8.0-models.jar \
target/appassembler/bin/nlpserver 8900 20 300 localhost 8901
