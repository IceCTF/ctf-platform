FROM ubuntu:trusty

ENV TERM xterm
ENV DEBIAN_FRONTEND noninteractive
ENV SHELL /bin/bash


RUN locale-gen en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8

# Install add-apt-repository
RUN sed -i 's/archive.ubuntu.com/is.archive.ubuntu.com/' /etc/apt/sources.list
RUN apt-get update -qq && apt-get install -y software-properties-common

# Install all dependencies
RUN mkdir /ctf_setup
WORKDIR /ctf_setup
ADD ./scripts/setup.sh setup.sh
ADD ./api/requirements.txt /ctf_setup/
ADD ./config/ctf.nginx /ctf_setup/
RUN ./setup.sh

# Create a mountpoint for the app
RUN mkdir /ctf

WORKDIR /ctf
