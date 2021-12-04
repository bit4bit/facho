#!/bin/sh

LIBXML2_VERSION=2.9.12

tar xf libxml2-${LIBXML2_VERSION}.tar.gz

mv libxml2-${LIBXML2_VERSION} libxml2

cd libxml2

wasiconfigure  ./configure --enable-static --without-http --without-ftp --without-modules --without-python --without-zlib --without-lzma --without-threads --host=x86_64

wasimake make clean
wasimake make -j4

mkdir -p ../vendor/libxml2/lib
mkdir -p ../vendor/libxml2/include
cp -r include/libxml2 ../vendor/libxml2/include
cp -r .libs/libxml2.a ../vendor/libxml2/lib
