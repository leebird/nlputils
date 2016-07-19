#!/usr/bin/env bash
set -e

# Set base folder.
SCRIPT_CWD=$PWD
CWD="$(dirname ${SCRIPT_CWD})"

# Remove dependencies.
cd ${CWD}/dep
rm -rf ./*

# Uninstall Python modules.
pip uninstall protobuf
pip uninstall grpcio
