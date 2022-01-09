/**
 * This file is part of facho.  The COPYRIGHT file at the top level of
 * this repository contains the full copyright notices and license terms.
 */

#ifndef XADES_H
#define XADES_H



#include <libxml/tree.h>

#define XMLSEC_NO_XSLT 1

#include <xmlsec/xmltree.h>
#include <xmlsec/transforms.h>
#include <xmlsec/xmldsig.h>
#include <xmlsec/base64.h>

#include "xmlsec1/errors_helpers.h"

#define xmlXadesAssert2(p, ret) \
  xmlSecAssert2(p, ret)

#define xmlXadesNodeNotFoundError(errorFunction, startNode, targetNodeName, errorObject) \
  xmlSecNodeNotFoundError(errorFunction, startNode, targetNodeName, errorObject)

#define xmlXadesXmlError2(errorFunction, errorObject, msg, param) \
  xmlSecXmlError2(errorFunction, errorObject, msg, param)

#define xmlXadesErrorsSafeString(msg) \
  xmlSecErrorsSafeString(msg)

#define xmlXadesInternalError(errorFunction, errorObject) \
  xmlSecInternalError(errorFunction, errorObject)

#define xmlXadesNodeAlreadyPresentError(parent, nodeName, errObject) \
  xmlSecNodeAlreadyPresentError(parent, nodeName, errObject)


typedef int xmlXadesSize;
typedef enum _XADES_DIGEST_METHOD{
  XADES_DIGEST_SHA256
} XADES_DIGEST_METHOD;

typedef int(*xmlXadesPolicyIdentifierContentCallback)(const xmlChar *policyId, xmlSecBuffer *);

typedef struct _xmlXadesPolicyIdentifierCtx  xmlXadesPolicyIdentifierCtx, *xmlXadesPolicyIdentifierCtxPtr;
struct _xmlXadesPolicyIdentifierCtx {
  xmlXadesPolicyIdentifierContentCallback contentCallback;
};
  
typedef struct _xmlXadesDSigCtx xmlXadesDSigCtx, *xmlXadesDSigCtxPtr;
struct _xmlXadesDSigCtx {
  xmlSecDSigCtxPtr dsigCtx;
  XADES_DIGEST_METHOD digestMethod;
  xmlXadesPolicyIdentifierCtxPtr policyCtx;
};

xmlXadesDSigCtxPtr
xmlXadesDSigCtxCreate(xmlSecDSigCtxPtr dsigCtx, XADES_DIGEST_METHOD digestMethod,  xmlXadesPolicyIdentifierCtxPtr policyCtx);

int
xmlXadesDSigCtxSign(xmlXadesDSigCtxPtr ctx, xmlNodePtr signNode);

int
xmlXadesDSigCtxDestroy(xmlXadesDSigCtxPtr ctx);

xmlNodePtr
xmlXadesTmplQualifyingPropertiesCreate(xmlDocPtr doc, xmlNodePtr signatureNode, const xmlChar *id);

xmlNodePtr
xmlXadesTmplAddSignedProperties(xmlNodePtr qualifyingPropertiesNode, const xmlChar* id);

xmlNodePtr
xmlXadesTmplAddSigningCertificate(xmlNodePtr parentNode, xmlSecTransformId digestMethodId);

xmlNodePtr
xmlXadesTmplAddCert(xmlNodePtr signingCertificateNode);

xmlNodePtr
xmlXadesTmplAddCertDigest(xmlNodePtr signingCertificateNode, const xmlChar *digestMethod, const xmlChar *digestValue);

xmlNodePtr
xmlXadesTmplAddSignedSignatureProperties(xmlNodePtr parentNode, struct tm* signingTime);

xmlNodePtr
xmlXadesTmplAddSignaturePolicyIdentifier(xmlNodePtr signedSignaturePropertiesNode);

xmlNodePtr
xmlXadesTmplAddSignaturePolicyId(xmlNodePtr signaturePolicyIdentifierNode);

xmlNodePtr
xmlXadesTmplAddSigPolicyId(xmlNodePtr signaturePolicyId, const xmlChar* identifier, const xmlChar *description);

xmlNodePtr
xmlXadesTmplAddSigPolicyHash(xmlNodePtr parentNode, xmlSecTransformId digestMethodId);

xmlNodePtr
xmlXadesTmplAddSignerRole(xmlNodePtr signedSignaturePropertiesNode, const xmlChar* role);

xmlNodePtr
xmlXadesTmplAddDigest(xmlNodePtr parentNode, const xmlChar *digestMethod, const xmlChar *digestValue);

xmlNodePtr
xmlXadesTmplAddIssuerSerial(xmlNodePtr certNode, const xmlChar *issuerName, const xmlChar *issuerNumber);

#endif //XADES_H
