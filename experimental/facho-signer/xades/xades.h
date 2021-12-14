#ifndef XADES_H
#define XADES_H

#include <libxml/tree.h>

#include <xmlsec/xmltree.h>
#include <xmlsec/transforms.h>
#include <xmlsec/app.h>
#include <xmlsec/xmldsig.h>
#include <xmlsec/openssl/x509.h>
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

static const xmlChar xmlXadesNodeQualifyingProperties[] = "QualifyingProperties";
static const xmlChar xmlXadesNodeSignedProperties[] = "SignedProperties";

static const xmlChar xmlXadesNodeSignedSignatureProperties[] = "SignedSignatureProperties";
static const xmlChar xmlXadesNodeSigningTime[] = "SigningTime";
static const xmlChar xmlXadesNodeSigningCertificate[] = "SigningCertificate";
static const xmlChar xmlXadesNodeCert[] = "Cert";
static const xmlChar xmlXadesNodeCertDigest[] = "CertDigest";
static const xmlChar xmlXadesNodeSignaturePolicyIdentifier[] = "SignaturePolicyIdentifier";
static const xmlChar xmlXadesNodeSignaturePolicyId[] = "SignaturePolicyId";
static const xmlChar xmlXadesNodeSigPolicyId[] = "SigPolicyId";
static const xmlChar xmlXadesNodeIdentifier[] = "Identifier";
static const xmlChar xmlXadesNodeDescription[] = "Description";
static const xmlChar xmlXadesNodeSigPolicyHash[] = "SigPolicyHash";

static const xmlChar xmlXadesNodeSignerRole[] = "SignerRole";
static const xmlChar xmlXadesNodeClaimedRoles[] = "ClaimedRoles";
static const xmlChar xmlXadesNodeClaimedRole[] = "ClaimedRole";
static const xmlChar xmlXadesNodeIssuerSerial[] = "IssuerSerial";
static const xmlChar xmlXadesNodeX509IssuerName[] = "X509IssuerName";
static const xmlChar xmlXadesNodeX509IssuerNumber[] = "X509IssuerNumber";
  
static const xmlChar xmlXadesDSigNs[] = "http://uri.etsi.org/01903/v1.3.2#";

typedef int xmlXadesSize;
typedef enum _XADES_DIGEST_METHOD{
  XADES_DIGEST_SHA256
} XADES_DIGEST_METHOD;

typedef int (*xmlXadesPolicyIdentifierContentCallback)(const xmlChar *policyId, xmlChar *content, xmlXadesSize *content_length);

typedef struct _xmlXadesPolicyIdentifierCtx *xmlXadesPolicyIdentifierCtxPtr;
struct _xmlXadesPolicyIdentifierCtx {
  XADES_DIGEST_METHOD digestMethod;
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
xmlXadesTmplAddIssuerSerial(xmlNodePtr certNode, const xmlChar *issuerName, const xmlChar *issuerNumber);

#endif //XADES_H
