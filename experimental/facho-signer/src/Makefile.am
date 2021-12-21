SOURCES = xades/xmlsec1/xmltree.c xades/xmlsec1/errors.c xades/templates.c xades/xades.c facho_signer.c

lib_LTLIBRARIES = libfachosigner.la
libfachosigner_la_SOURCES = $(LTDL_SOURCE_FILES) $(SOURCES)
libfachosigner_la_CFLAGS = $(OPENSSL_CFLAGS) $(XMLSEC1_CFLAGS) -DXMLSEC_NOT_CRYPTO_DYNAMIC_LOADING
libfachosigner_la_LDFLAGS = $(OPENSSL_LIBS) $(LIBLTDL) $(XMLSEC1_LIBS)

bin_PROGRAMS = facho_signer
facho_signer_SOURCES = main.c
facho_signer_CFLAGS = $(OPENSSL_CFLAGS) $(XMLSEC1_CFLAGS) -DXMLSEC_NOT_CRYPTO_DYNAMIC_LOADING
facho_signer_LDADD = libfachosigner.la

