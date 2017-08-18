#!/usr/bin/env bash

# Set working folder, which is the root folder of the nlputils project.
SCRIPT_PATH="$(readlink -f ${BASH_SOURCE})"
echo "Common path script path: ${SCRIPT_PATH}"

# The path storing the nlputils project.
ROOT_PATH="$(dirname $(dirname ${SCRIPT_PATH}))"
echo "nlputils root path: ${ROOT_PATH}"

# The path storing dependency libraries, which will be downloaded using the
# following lines.
DEPENDENCY_PATH="${ROOT_PATH}/dep"
echo "Dependency path: ${DEPENDENCY_PATH}"

