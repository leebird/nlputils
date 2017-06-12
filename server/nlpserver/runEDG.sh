#!/usr/bin/env bash

CLASSPATH_PREFIX=lib/stanford-corenlp-3.6.0-models.jar \
target/appassembler/bin/nlpserver 8902 20 300 localhost 8901
