#!/usr/bin/env bash
# BLLIP_PROC_NUM is the number of bllip parser processes.
docker pull leebird/nlputils
docker run --init --network=host -d -e "BLLIP_PROC_NUM=1" leebird/nlputils
