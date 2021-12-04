#!/bin/sh
# TOMADO DE: https://github.com/voltbuilder/openssl-wasm

OPENSSL_VERSION=1.1.1l

# get the source
tar xf openssl-${OPENSSL_VERSION}.tar.gz

patch -p0 < openssl-${OPENSSL_VERSION}.patch

cd openssl-${OPENSSL_VERSION}
make clean

set -e

# why ./Configure instead of ./config? We want to force using the generic gcc profile which is more conservative than linux-x32
# -no-sock - we don't have sockets in WASI
# new -no-ui-console - sdk 12 has no termios???
# check in 12 -DHAVE_FORK=0 - no fork() in WASI
# new -D_WASI_EMULATED_MMAN - works with the library below to enable WASI mman emulation
# new -D_WASI_EMULATED_SIGNAL - with sdk 12
# new -DOPENSSL_NO_SECURE_MEMORY - wasi doesn't have secure mem (madvise, mlock, etc...)
# new -DNO_SYSLOG - get rid of need for patch above
# --with-rand-seed=getrandom (needed to force using getentropy because WASI has no /dev/random or getrandom)
wasiconfigure ./Configure gcc -no-sock -no-ui-console -DHAVE_FORK=0 -D_WASI_EMULATED_MMAN -D_WASI_EMULATED_SIGNAL -DOPENSSL_NO_SECURE_MEMORY -DNO_SYSLOG --with-rand-seed=getrandom

# enables stuff from mman.h (see define above) also add -lwasi-emulated-signal
#sed -i -e "s/CNF_EX_LIBS=/CNF_EX_LIBS=-lwasi-emulated-mman -lwasi-emulated-signal /g" Makefile

# build!
wasimake make -j4 build_generated libssl.a libcrypto.a

rm -rf ../vendor/openssl/include
mkdir -p ../vendor/openssl/include
cp -R include/openssl ../vendor/openssl/include

mkdir -p ../vendor/openssl/lib/
cp libssl.a ../vendor/openssl/lib/
cp libcrypto.a ../vendor/openssl/lib/

exit 0
