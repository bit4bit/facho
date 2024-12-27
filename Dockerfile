# DERIVADO DE https://alextereshenkov.github.io/run-python-tests-with-tox-in-docker.html
FROM ubuntu:24.04

RUN apt-get -qq update

RUN apt install software-properties-common -y \
    && add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y --no-install-recommends \
  python3.9 python3.9-distutils python3.9-dev \
  python3.10 python3.10-distutils python3.10-dev \
  python3.11 python3.11-distutils python3.11-dev \
  python3.12 python3-setuptools python3.12-dev \
  wget \
  ca-certificates

RUN wget https://bootstrap.pypa.io/get-pip.py \
  && python3.9 get-pip.py pip==23.2.1 --break-system-packages \
  && python3.10 get-pip.py pip==23.2.1 --break-system-packages \
  && python3.11 get-pip.py pip==23.2.1 --break-system-packages \
  && python3.12 get-pip.py pip==23.2.1  --break-system-packages \
  && rm get-pip.py

RUN apt-get install -y --no-install-recommends \
        libxml2-dev \
        libxmlsec1-dev \
        build-essential \
        zip

RUN python3.9 --version
RUN python3.10 --version
RUN python3.11 --version
RUN python3.12 --version

RUN pip3.9 install setuptools setuptools-rust
RUN pip3.10 install setuptools setuptools-rust
RUN pip3.11 install setuptools setuptools-rust --break-system-packages
RUN pip3.12 install setuptools setuptools-rust --break-system-packages

RUN pip3 install tox pytest --break-system-packages
