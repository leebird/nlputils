FROM ubuntu:16.04
MAINTAINER Gang Li <leemagpie@gmail.com>

RUN apt update && apt upgrade -y

RUN apt install build-essential -y

RUN apt install python python-pip -y

# Install java 8.
RUN apt install -y software-properties-common && \
    add-apt-repository ppa:webupd8team/java -y && \
    apt update && \
    echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
    apt install -y oracle-java8-installer && \
    apt clean

RUN apt install git -y
RUN apt install curl -y
RUN apt install unzip -y
RUN apt install dh-autoreconf -y
RUN apt install maven -y
RUN apt install supervisor -y

RUN pip install --upgrade pip

RUN mkdir /nlputils

# Separate copy for better caching.
COPY scripts /nlputils/scripts

# We need bash to initialize nlputils.
# These take a long time, run them first.
RUN ln -snf /bin/bash /bin/sh
RUN . /nlputils/scripts/export_path.sh && cd /nlputils/ && bash scripts/init.sh

COPY proto /nlputils/proto
COPY protolib /nlputils/protolib
RUN . /nlputils/scripts/export_path.sh && cd /nlputils/ && bash scripts/compile_document_proto.sh

COPY server/bllip /nlputils/server/bllip
COPY server/nlpserver /nlputils/server/nlpserver
COPY utils /nlputils/utils
COPY visual /nlputils/visual
COPY test /nlputils/test

# Init modules.
RUN cd /nlputils/server/nlpserver/ && sh init.sh
RUN cd /nlputils/server/bllip && python init.py
RUN cd /nlputils/visual && sh init.sh

COPY docker/supervisord.conf /etc/supervisord.conf

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
