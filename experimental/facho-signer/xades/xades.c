#include "xades.h"

#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <openssl/bio.h>
#include <openssl/asn1.h>
#include <openssl/bn.h>

#include <string.h>
#include <ctype.h>

static xmlNodePtr
xmlXadesXPathFirstElement(xmlDocPtr doc, const xmlChar *xpath) {
  xmlXPathContextPtr xpathCtx;
  xmlXPathObjectPtr xpathResult;
  xmlNodePtr node;

  // obtener QualifyingProteries

  xpathCtx = xmlXPathNewContext(doc);
  /* register namespaces */
  // TOMADO DE: xmlsec1/src/xpath.c
  for(xmlNsPtr ns = xmlDocGetRootElement(doc)->nsDef; ns != NULL; ns = ns->next) {
    /* check that we have no other namespace with same prefix already */
    if((ns->prefix != NULL) && (xmlXPathNsLookup(xpathCtx, ns->prefix) == NULL)){
      int ret = xmlXPathRegisterNs(xpathCtx, ns->prefix, ns->href);
      if(ret != 0) {
        xmlXadesXmlError2("xmlXPathRegisterNs", NULL,
                          "prefix=%s", xmlSecErrorsSafeString(ns->prefix));
        return(NULL);
      }
    }
  }


  xpathResult = xmlXPathEvalExpression(BAD_CAST "//ds:Object/xades:QualifyingProperties[1]", xpathCtx);
  if ( xmlXPathNodeSetIsEmpty( xpathResult->nodesetval ) ) {
    xmlXadesInternalError("can't find ds:Signature/ds:Object/xades:QualifyingProperties \n", NULL);
    xmlXPathFreeObject(xpathResult);
    return(NULL);
  }

  // obtener puntero a nodo
  node = xpathResult->nodesetval->nodeTab[0];
  if ( node->type != XML_ELEMENT_NODE ) {
    xmlXadesInternalError("expected element QualifyingProperties\n", NULL);
    return(NULL);
  }

  return(node);
}

xmlXadesDSigCtxPtr
xmlXadesDSigCtxCreate(xmlSecDSigCtxPtr dsigCtx) {
  xmlXadesDSigCtxPtr ctx = NULL;

  ctx = malloc(sizeof(xmlXadesDSigCtx));
  if ( ctx == NULL ) {
    return(NULL);
  }

  ctx->dsigCtx = dsigCtx;
  return ctx;
}

int
xmlXadesDSigCtxSign(xmlXadesDSigCtxPtr ctx, xmlNodePtr signNode) {
  xmlNodePtr signingCertificateNode = NULL;
  xmlSecKeyDataPtr keyDataX509;
  xmlSecSize certsSize;

  signingCertificateNode = xmlXadesXPathFirstElement(signNode->doc, BAD_CAST "//ds:Object/xades:QualifyingProperties//xades:SigningCertificate[1]");
  if ( signingCertificateNode == NULL ) {
    return(-1);
  }

  keyDataX509 = xmlSecKeyEnsureData(ctx->dsigCtx->signKey, xmlSecKeyDataX509Id);
  if ( keyDataX509 == NULL ) {
    xmlXadesInternalError("failed to get X509.\n", NULL);
    return(-1);
  }

  certsSize = xmlSecOpenSSLKeyDataX509GetCertsSize(keyDataX509);
  for (xmlSecSize i = 0; i < certsSize; i++) {
    // calculamos el digest del certificado
    unsigned char md[EVP_MAX_MD_SIZE];
    unsigned int md_n;
    // TODO(bit4bit) podemos obtener el digest de openssl por medio de la transformacion? o se puede usar la transformacion para generar el digest?
    xmlChar *digestMethod = (xmlChar *)xmlSecTransformSha256Id->href;
    const EVP_MD *digest = EVP_sha256();

    X509 *cert = xmlSecOpenSSLKeyDataX509GetCert(keyDataX509, i);
    if ( cert == NULL ) {
      xmlXadesInternalError("openssl: failed to get X509 cert.\n", NULL);
      return(-1);
    }

    X509_digest(cert, digest, md, &md_n);
    xmlChar *digestValue = xmlSecBase64Encode(md, md_n, 0);

    xmlNodePtr certNode = xmlXadesTmplAddCert(signingCertificateNode);
    if ( certNode == NULL ) {
      xmlXadesInternalError("xmlXadesTmplAddCert(signingCertificateNode)\n", NULL);
      return(-1);
    }

    // adicionamos digest 
    xmlXadesTmplAddCertDigest(certNode,
                              digestMethod,
                              digestValue);

    char *issuerName = X509_NAME_oneline(X509_get_issuer_name(cert), NULL, 0);

    /* TODO(bit4bit) formatear?
    char *issuerNamePtr = issuerName;
    
    for(issuerNamePtr = strchr(issuerNamePtr, '/'); issuerNamePtr != NULL; issuerNamePtr = strchr(issuerNamePtr, '/')) {
      if (issuerNamePtr == issuerName) {
        issuerName += 1;
      } else {
        *issuerNamePtr = ',';
      }
      }*/

    ASN1_INTEGER *serial = X509_get_serialNumber(cert);
    BIGNUM *bn = ASN1_INTEGER_to_BN(serial, NULL);
    if ( bn == NULL ) {
      xmlXadesInternalError("unable to convert ASN1_INTEGER_to_BN to BN\n", NULL);
      return(-1);
    }
    char *issuerNumber = BN_bn2dec(bn);
    if ( issuerNumber == NULL ) {
      xmlXadesInternalError("unable to convert BN to decimal string\n", NULL);
      return(-1);
    }

    if (xmlXadesTmplAddIssuerSerial(certNode, BAD_CAST issuerName, BAD_CAST issuerNumber) == NULL) {
      xmlXadesInternalError("xmlXadesTmplAddIssuerSerial", NULL);
      return(-1);
    }
    BN_free(bn);
    OPENSSL_free(issuerNumber);
  }

  return xmlSecDSigCtxSign(ctx->dsigCtx, signNode);
}


int
xmlXadesDSigCtxDestroy(xmlXadesDSigCtxPtr ctx) {
  if ( ctx == NULL ) {
    return(-1);
  }

  free(ctx);
  return(0);
}
