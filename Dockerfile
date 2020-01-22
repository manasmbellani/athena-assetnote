#!/bin/bash
FROM alpine:latest
MAINTAINER manasbellani

# Install all the apt-gettable modules one-by-one
# Obscure Installed packages:
#   psmisc, for  using killall
RUN apk add \
    sudo \
    git \
    vim \
    psmisc \
    python3 \
    jq \
    curl \
    bash

# Upgrade pip 
RUN python3 -m pip install --upgrade pip

# Install packages
RUN python3 -m pip install requests

# Install the .vimrc file
RUN curl -L -s -k https://gist.githubusercontent.com/manasmbellani/9b9e6ab12510ccaa82aa31650a804a9d/raw/8787db0d170dd862ea23926ac61d9905bc1cf873/vimrc -o /root/.vimrc

# Start within this shared directory
WORKDIR /opt/athena-assetnote
