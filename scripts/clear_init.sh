#!/usr/bin/env bash

set -e
# Get path information.
source "$(dirname $BASH_SOURCE)"/utils.sh

# Remove dependencies.
echo "Remove libraries in ${DEPENDENCY_PATH}"
cd ${DEPENDENCY_PATH}
rm -rf ./*

# Uninstall Python modules.
pip uninstall protobuf
pip uninstall grpcio
pip uninstall glog
