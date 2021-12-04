#!/bin/sh

XMLSEC1_VERSION=1.2.33

tar xf xmlsec1-${XMLSEC1_VERSION}.tar.gz

cd xmlsec1-${XMLSEC1_VERSION}

cp -r ../libxml2 .
cp -r ../vendor .

wasiconfigure ./configure --with-libxml-src=`pwd`/libxml2 --with-openssl=`pwd`/vendor/openssl  --enable-static-linking  --disable-folders-search --disable-apps --disable-apps-crypto-dl --disable-crypto-dl

wasimake make -j4
