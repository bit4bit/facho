# DERIVADO DE https://alextereshenkov.github.io/run-python-tests-with-tox-in-docker.html
FROM ubuntu:18.04

RUN apt-get -qq update

RUN apt install software-properties-common -y \
    && add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y --no-install-recommends \
  python3.7 python3.7-distutils python3.7-dev \
  python3.8 python3.8-distutils python3.8-dev \
  python3.9 python3.9-distutils python3.9-dev \
  python3.10 python3.10-distutils python3.10-dev \
  wget \
  ca-certificates

RUN wget https://bootstrap.pypa.io/get-pip.py \
  && python3.7 get-pip.py pip==22.2.2 \
  && python3.8 get-pip.py pip==22.2.2 \
  && python3.9 get-pip.py pip==22.2.2 \
  && python3.10 get-pip.py pip==22.2.2 \
  && rm get-pip.py

RUN apt-get install -y --no-install-recommends \
        libxml2-dev \
        libxmlsec1-dev \
        build-essential \
        zip

RUN python3.7 --version
RUN python3.8 --version
RUN python3.9 --version
RUN python3.10 --version

RUN pip3.7 install setuptools setuptools-rust
RUN pip3.8 install setuptools setuptools-rust
RUN pip3.9 install setuptools setuptools-rust
RUN pip3.10 install setuptools setuptools-rust

RUN pip3 install tox pytest
