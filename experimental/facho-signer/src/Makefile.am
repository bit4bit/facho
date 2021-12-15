bin_PROGRAMS = facho_signer
facho_signer_SOURCES = xades/xmlsec1/xmltree.c xades/xmlsec1/errors.c xades/templates.c xades/xades.c facho_signer.c
facho_signer_CFLAGS = $(XMLSEC1_CFLAGS) -DXMLSEC_NOT_CRYPTO_DYNAMIC_LOADING
facho_signer_LDADD = $(XMLSEC1_LIBS)
