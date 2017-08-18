#!/usr/bin/env bash
# BLLIP_PROC_NUM is the number of bllip parser processes.
docker run --init --network=host -e "BLLIP_PROC_NUM=1" leebird/nlputils
