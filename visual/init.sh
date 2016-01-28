#!/usr/bin/env bash

# Download the brat annotation tool.
rm -rf brat
wget http://weaver.nlplab.org/~brat/releases/brat-v1.3_Crunchy_Frog.tar.gz
tar -zxvf brat-v1.3_Crunchy_Frog.tar.gz && mv brat-v1.3_Crunchy_Frog brat

# Install flask
pip install flask