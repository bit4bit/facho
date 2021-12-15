#include "xades.h"

#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <openssl/bio.h>
#include <openssl/asn1.h>
#include <openssl/bn.h>

#include <xmlsec/buffer.h>
#include <string.h>
#include <ctype.h>


static xmlChar *
xmlXadesSha256DigestValueInBase64(const unsigned char *message, size_t message_len);

static xmlNodePtr
xmlXadesXPathFirstElement(xmlDocPtr doc, const xmlChar *xpath);

xmlXadesDSigCtxPtr
xmlXadesDSigCtxCreate(xmlSecDSigCtxPtr dsigCtx, XADES_DIGEST_METHOD digestMethod, xmlXadesPolicyIdentifierCtxPtr policyCtx) {
  xmlXadesDSigCtxPtr ctx = NULL;

  ctx = malloc(sizeof(xmlXadesDSigCtx));
  if ( ctx == NULL ) {
    return(NULL);
  }

  ctx->dsigCtx = dsigCtx;
  ctx->digestMethod = digestMethod;
  ctx->policyCtx = policyCtx;
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
    xmlChar *digestMethod = NULL;
    EVP_MD *digest = NULL;

    switch(ctx->digestMethod) {
    case XADES_DIGEST_SHA256:
      digestMethod = (xmlChar *)xmlSecTransformSha256Id->href;
      digest = (EVP_MD *) EVP_sha256();
      break;
    default:
      xmlXadesInternalError("xmlXadesDSigCtxSign not known how to handle digest method.\n", NULL);
      return(-1);
    }

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

  // digest de policy identifier
  xmlNodePtr sigPolicyId = xmlXadesXPathFirstElement(signNode->doc, BAD_CAST "//xades:SigPolicyId/xades:Identifier[1]");
  if ( sigPolicyId == NULL ) {
    xmlXadesInternalError("xmlXadesXPathFirstElement(xades:SigPolicyId/xades:Identifier\n", NULL);
    return(-1);
  }

  if ( ctx->policyCtx == NULL ) {
    xmlXadesInternalError("not found policy context.\n", NULL);
    return(-1);
  }

  if ( ctx->policyCtx != NULL ) {


    if ( ctx->policyCtx->contentCallback == NULL ) {
      xmlXadesInternalError("not found policy content callback.\n", NULL);
      return(-1);
    }


    xmlSecTransformCtxPtr transformCtx = xmlSecTransformCtxCreate();
    if (transformCtx == NULL ) {
      xmlXadesInternalError("xmlSecTransformCtxCreate().\n", NULL);
      return(-1);
    }

    // elemento del digest
    xmlNodePtr sigPolicyHashDigestMethod = xmlXadesXPathFirstElement(signNode->doc, BAD_CAST "//xades:SigPolicyHash/ds:DigestMethod[1]");
    if ( sigPolicyHashDigestMethod == NULL ) {
      xmlXadesInternalError("xmlXadesXPathFirstElement(xades:SigPolicyHash/xades:DigestMethod\n", NULL);
      return(-1);
    }
    xmlSecTransformPtr transformPolicyDigestMethod = xmlSecTransformNodeRead(sigPolicyHashDigestMethod,
                                                                             xmlSecTransformUsageDigestMethod,
                                                                             transformCtx);
    if ( transformPolicyDigestMethod == NULL ) {
      xmlXadesInternalError("xmlSecTransformNodeRead\n", NULL);
      xmlFreeNode(sigPolicyHashDigestMethod);
      return(-1);
    }

    if ( xmlSecTransformCheckId(transformPolicyDigestMethod, xmlSecTransformSha256Id) == 0 ) {
      xmlXadesInternalError("sigPolicyHash only support sha256 digest method .\n", NULL);
      xmlFreeNode(sigPolicyHashDigestMethod);
      return(-1);
    }

    // TODO(bit4bit) podemos usar xmlSecTransform para calcular el digest?
    xmlNodePtr sigPolicyHashNode = xmlXadesXPathFirstElement(signNode->doc, BAD_CAST "//xades:SigPolicyHash[1]");
    if ( sigPolicyHashNode == NULL ) {
      xmlXadesInternalError("failed to find sigPolicyHash node.\n", NULL);
      xmlFreeNode(sigPolicyHashDigestMethod);
      return(-1);
    }

    // obtenemos contenido de la policy
    xmlChar *identifier = xmlNodeListGetString(signNode->doc, sigPolicyId->xmlChildrenNode, 1);
    xmlSecBufferPtr policyContent = xmlSecBufferCreate(1024);
    ;
    if ( (ctx->policyCtx->contentCallback)(identifier, policyContent) < 0 ) {
      xmlXadesInternalError("policyContext callback fails.\n", NULL);
      xmlFree(identifier);
      return(-1);
    }
    xmlFree(identifier);

    xmlChar *policyHashValue = xmlXadesSha256DigestValueInBase64(xmlSecBufferGetData(policyContent),
                                                                 xmlSecBufferGetSize(policyContent));

    xmlSecBufferDestroy(policyContent);
    xmlXadesTmplAddDigest(sigPolicyHashNode, NULL, policyHashValue);
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

xmlNodePtr
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


  xpathResult = xmlXPathEvalExpression(xpath, xpathCtx);
  if ( xmlXPathNodeSetIsEmpty( xpathResult->nodesetval ) ) {
    xmlXadesInternalError("can't find %s \n", xpath);
    xmlXPathFreeObject(xpathResult);
    return(NULL);
  }

  // obtener puntero a nodo
  node = xpathResult->nodesetval->nodeTab[0];
  if ( node->type != XML_ELEMENT_NODE ) {
    xmlXadesInternalError("expected element\n", NULL);
    return(NULL);
  }

  return(node);
}

static xmlChar *
xmlXadesSha256DigestValueInBase64(const unsigned char *message, size_t message_len)
{
  unsigned char digest[2048];
  unsigned int digest_len;
  EVP_MD_CTX *mdctx;

  if((mdctx = EVP_MD_CTX_new()) == NULL) {
    xmlXadesInternalError("EVP_MD_CTX_new().\n", NULL);
    return(NULL);
  }

  if(1 != EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL)) {
    xmlXadesInternalError("EVP_DigestInit_ex().\n", NULL);
    return(NULL);
  }

  if(1 != EVP_DigestUpdate(mdctx, message, message_len)) {
    xmlXadesInternalError("EVP_DigestUpdate().\n", NULL);
    return(NULL);
  }

  if(1 != EVP_DigestFinal_ex(mdctx, digest, &digest_len)) {
    xmlXadesInternalError("EVP_DigestFinal_ex().\n", NULL);
    return(NULL);
  }

  EVP_MD_CTX_free(mdctx);
  return(xmlSecBase64Encode(digest, digest_len, 0));
}
