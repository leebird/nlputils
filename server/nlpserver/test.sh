#!/usr/bin/env bash

CLASSPATH_PREFIX=lib/stanford-corenlp-3.6.0-models.jar \
target/appassembler/bin/test_stanford

# This requires the bllip client running on localhost:8901.
CLASSPATH_PREFIX=lib/stanford-corenlp-3.6.0-models.jar \
target/appassembler/bin/test_bllipclient
