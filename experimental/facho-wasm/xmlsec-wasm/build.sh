#!/bin/sh

set -ex

sh build_openssl.sh
sh build_libxml2.sh
sh build_xmlsec.sh
