#!/usr/bin/env bash

set -e
# Get path information.
source "$(dirname $BASH_SOURCE)"/common_path.sh

# Remove dependencies.
echo "Remove libraries in ${DEPENDENCY_PATH}"
cd ${DEPENDENCY_PATH}
rm -rf ./*

# Uninstall Python modules.
pip uninstall -y protobuf
pip uninstall -y grpcio
pip uninstall -y glog
