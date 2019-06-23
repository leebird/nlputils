#!/usr/bin/env bash
# To stop: docker rm -f CONTAINER_ID
# To clean unused volumns: docker volume rm $(docker volume ls -qf dangling=true)
# To see current container logs (useful for checking if the server is ready): docker logs CONTAINER_ID

# BLLIP_PROC_NUM: Number of BLLIP parser processes for parallel processing.
# BLLIP_PORT: BLLIP parser server port.
# STANFORD_VERSION: Stanford CoreNLP version.
# STANFORD_PORT: Stanford CoreNLP server port (main port used by the client codes)
# VISUAL_PORT: Visual web interface port.

docker pull leebird/nlputils
docker run --name=nlputils_server --init --network=host -d \
       -e BLLIP_PROC_NUM=10 \
       -e BLLIP_PORT=8901 \
       -e STANFORD_VERSION=3.6.0 \
       -e STANFORD_PORT=8900 \
       -e VISUAL_PORT=5000 \
       leebird/nlputils
