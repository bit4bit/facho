#!/bin/sh

LIBXML2_VERSION=2.9.12

tar xf libxml2-${LIBXML2_VERSION}.tar.gz

mv libxml2-${LIBXML2_VERSION} libxml2

pushd libxml2

wasiconfigure  ./configure --enable-static --without-http --without-ftp --without-modules --without-python --without-zlib --without-lzma --without-threads --host=x86_64

wasimake make clean
wasimake make -j4

popd

mkdir -p vendor/libxml2/lib
mkdir -p vendor/libxml2/include
cp -r libxml2/include/libxml2 vendor/libxml2/include
cp -r libxml2/.libs/libxml2.a vendor/libxml2/lib
