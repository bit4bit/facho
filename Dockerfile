# DERIVADO DE https://alextereshenkov.github.io/run-python-tests-with-tox-in-docker.html
FROM ubuntu:18.04

RUN apt-get -qq update
RUN apt-get install -y --no-install-recommends \
  python3.7 python3.7-distutils python3.7-dev \
  python3.8 python3.8-distutils python3.8-dev \
  wget \
  ca-certificates

RUN wget https://bootstrap.pypa.io/get-pip.py \
  && python3 get-pip.py pip==21.3 \
  && python3.7 get-pip.py pip==21.3 \
  && python3.8 get-pip.py pip==21.3 \
  && rm get-pip.py

RUN apt-get install -y --no-install-recommends \
        libxml2-dev \
        libxmlsec1-dev \
        build-essential

RUN python3.6 --version
RUN python3.7 --version
RUN python3.8 --version

RUN pip3.6 install setuptools setuptools-rust
RUN pip3.7 install setuptools setuptools-rust
RUN pip3.8 install setuptools setuptools-rust

RUN pip3 install tox pytest
