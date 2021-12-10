#include "xades.h"

int
xmlFachoAppSign(xmlDocPtr doc,
                xmlSecTransformId hashMethodId) {
  xmlXadesAssert2(doc != NULL, NULL);
  xmlNodePtr cur;
  xmlNodePtr signedSignaturePropertiesNode;
  xmlNodePtr signaturePolicyIdentifierNode;
  xmlNodePtr signaturePolicyIdNode;
  xmlChar* signedPropertiesId = BAD_CAST "ref1-signedprops";
  time_t now = time(NULL);
  
  cur = xmlXadesTmplQualifyingPropertiesCreateNsPref(doc, "qualify-ref1", BAD_CAST "ds");
  if (cur == NULL) {
    return(-1);
  }

  cur = xmlXadesTmplAddSignedProperties(cur, signedPropertiesId);
  if (cur == NULL) {
    return(-1);
  }

  signedSignaturePropertiesNode = xmlXadesTmplAddSignedSignatureProperties(cur,  now);
  if (signedSignaturePropertiesNode == NULL) {
    return(-1);
  }

  // addSigningCertificate

  // addSignaturePolicyIdentifier

  signaturePolicyIdNode = xmlXadesAddChildRecursiveNs(signedSignaturePropertiesNode, BAD_CAST "SignaturePolicyIdentifier/SignaturePolicyId", xmlXadesDSigNs)
  if (signaturePolicyIdNode == NULL) {
    return(-1);
  }
  cur = xmlXadesTmplAddSigPolicyId(signaturePolicyIdNode, identifier, description, hashMethodId);
  if (cur == NULL) {
    return(-1);
  }
  // SignaturePolicyIdentifier/SignaturePolicyId/SigPolicyHash
  cur = xmlXadesTmplAddSigPolicyHash(signaturePolicyIdNode);
  if (cur == NULL) {
    return(-1);
  }
  cur = xmlXadesTmplAddDigest(cur, hashMethodId);
  if (cur == NULL) {
    return(-1);
  }

  // addSignerRole
  xmlXadesTmplAddSignerRole(signedSignaturePropertiesNode, BAD_CAST "supplier");
  
  cur = xmlSecTmplSignatureAddReference(xmlDocGetRootElement(doc),
                                        hashMethodId,
                                        signedPropertiesId,
                                        NULL, NULL);
}
