cp ../vendor/openssl/lib/*.a .
cp ../xmlsec1-1.2.33/src/.libs/*.a .
cp ../xmlsec1-1.2.33/src/openssl/.libs/*.a .
cp ../libxml2/.libs/libxml2.a .

mkdir -p include

cp -r ../libxml2/include/libxml include/
cp -r ../xmlsec1-1.2.33/include/xmlsec include/
cp -r ../vendor/openssl/include/* include/

wasicc -Iinclude libxml2.a libcrypto.a libssl.a libxmlsec1.a libxmlsec1-openssl.a sign.c 
