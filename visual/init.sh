#!/usr/bin/env bash

# Download the brat annotation tool.
#rm -rf brat
if [ ! -d "brat" ]; then
	# Remember to comment out that 5000 ms option.
	wget http://weaver.nlplab.org/~brat/releases/brat-v1.3_Crunchy_Frog.tar.gz
	tar -zxvf brat-v1.3_Crunchy_Frog.tar.gz && mv brat-v1.3_Crunchy_Frog brat
fi

# Install flask
pip install flask
