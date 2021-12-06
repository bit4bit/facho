#include <time.h>

#include "xades.h"

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

xmlNodePtr
xmlXadesTmplQualifyingPropertiesCreateNsPref(xmlDocPtr doc, const xmlChar* id, const xmlChar* nsPrefix) {
  xmlNodePtr qualifyingPropertiesNode;
  xmlNodePtr cur;
  xmlNsPtr ns;

  // crear nodo
  qualifyingPropertiesNode = xmlNewDocNode(doc, NULL, xmlXadesNodeQualifyingProperties, NULL);
  if (qualifyingPropertiesNode == NULL) {
    xmlXadesXmlError2("xmlNewDocNode", NULL, "node=%s", xmlXadesErrorsSafeString(xmlXadesNodeQualifyingProperties));
    return(NULL);
  }

  // crear namespace y asignar
  ns = xmlNewNs(qualifyingPropertiesNode, xmlXadesDSigNs, nsPrefix);
  if (ns == NULL) {
    xmlXadesXmlError2("xmlNewNs", NULL,
                   "ns=%s", xmlXadesErrorsSafeString(xmlXadesDSigNs));
    xmlFreeNode(qualifyingPropertiesNode);
    return(NULL);
  }
  xmlSetNs(qualifyingPropertiesNode, ns);

  if (id != NULL) {
    xmlSetProp(qualifyingPropertiesNode, BAD_CAST "id", id);
  }

  // add SignedProperties
  cur = xmlSecAddChild(qualifyingPropertiesNode, xmlXadesNodeSignedProperties, xmlXadesDSigNs);
  if (cur == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSignedProperties)", NULL);
    xmlFreeNode(qualifyingPropertiesNode);
    return(NULL);
  }


  return (qualifyingPropertiesNode);
}


xmlNodePtr
xmlXadesTmplAddSignedSignatureProperties(xmlNodePtr parentNode, const xmlChar* id, struct tm* signingTime) {
  xmlNodePtr cur;
  xmlNodePtr node;
  xmlNodePtr signedPropertiesNode;

  xmlXadesAssert2(parentNode != NULL, NULL);
  
  signedPropertiesNode = xmlSecFindChild(parentNode, xmlXadesNodeSignedProperties, xmlXadesDSigNs);
  if (signedPropertiesNode == NULL) {
    xmlXadesNodeNotFoundError("xmlSecFindChild", parentNode,
                              xmlXadesNodeSignedProperties, NULL);
    return(NULL);
  }

  // add SignedSignatureProperties
  node = xmlSecAddChild(signedPropertiesNode, xmlXadesNodeSignedSignatureProperties, xmlXadesDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSignedSignatureProperties)", NULL);
    return(NULL);
  }

  if (id != NULL) {
    xmlSetProp(node, BAD_CAST "id", id);
  }

  // add SignigTime
  cur = xmlSecAddChild(node, xmlXadesNodeSigningTime, xmlXadesDSigNs);
  if (cur == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSigningTime)", NULL);
    xmlFreeNode(node);
    return(NULL);
  }

  {
    int ret;
    char strtime[200];

    if (strftime(strtime, sizeof(strtime), "%Y-%m-%dT%T", signingTime) == 0) {
      xmlXadesInternalError("strftime", NULL);
      xmlFreeNode(cur);
      xmlFreeNode(node);
      return(NULL);
    }

    ret = xmlSecNodeEncodeAndSetContent(cur, BAD_CAST strtime);
    if (ret < 0) {
      xmlXadesInternalError("xmlSecNodeEncodeAndSetContent", NULL);
      xmlFreeNode(cur);
      xmlFreeNode(node);
      return(NULL);
    }
  }

  // addSigningCertificate
  cur = xmlSecAddChild(node, xmlXadesNodeSigningCertificate, xmlXadesDSigNs);
  if (cur == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSigningCertificate)", NULL);
    xmlFreeNode(node);
    return(NULL);
  }
  
  return(node);
}

xmlNodePtr
xmlXadesTmplAddSigningCertificate(xmlNodePtr signedSignaturePropertiesNode) {
  xmlNodePtr node;
  
  xmlXadesAssert2(signedSignaturePropertiesNode != NULL, NULL);
  if (xmlSecFindChild(signedSignaturePropertiesNode, xmlXadesNodeSigningCertificate, xmlXadesDSigNs) != NULL) {
    xmlXadesNodeAlreadyPresentError(signedSignaturePropertiesNode, xmlXadesNodeSigningCertificate, NULL);
    return(NULL);
  }

  node = xmlSecAddChild(signedSignaturePropertiesNode, xmlXadesNodeSigningCertificate, xmlXadesDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlsecAddChild(xmlXadesNodeSigningCertificate)", NULL);
    return(NULL);
  }

  return(node);
}

xmlNodePtr
xmlXadesTmplAddCert(xmlNodePtr parentNode) {
  xmlNodePtr node;

  xmlXadesAssert2(parentNode != NULL, NULL);
  if (xmlSecFindChild(parentNode, xmlXadesNodeCertificate, xmlXadesDSigNs) != NULL) {
    xmlXadesNodeAlreadyPresentError(parentNode, xmlXadesNodeCertificate, NULL);
    return(NULL);
  }

  node = xmlSecAddChild(parentNode, xmlXadesNodeCertificate, xmlXadesDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeCertificate)", NULL);
    return(NULL);
  }

  return(node);
}

xmlNodePtr
xmlXadesTmplAddSignaturePolicyIdentifierSignaturePolicyId(xmlNodePtr signedSignaturePropertiesNode) {
  xmlNodePtr cur;
  
  xmlXadesAssert2(signedSignaturePropertiesNode != NULL, NULL);
  if (xmlSecFindChild(signedSignaturePropertiesNode, xmlXadesNodeSigningCertificate, xmlXadesDSigNs) != NULL) {
    xmlXadesNodeAlreadyPresentError(signedSignaturePropertiesNode, xmlXadesNodeSigningCertificate, NULL);
    return(NULL);
  }

  cur = xmlSecAddChild(signedSignaturePropertiesNode, xmlXadesNodeSignaturePolicyIdentifier, xmlXadesDSigNs);
  if (cur == NULL) {
    xmlXadesInternalError("xmlsecAddChild(xmlXadesNodeSignaturePolicyIdentifier)", NULL);
    return(NULL);
  }

  cur = xmlSecAddChild(cur, xmlXadesNodeSignaturePolicyId, xmlXadesDSigNs);
  if (cur == NULL) {
    xmlXadesInternalError("xmlsecAddChild(xmlXadesNodeSignaturePolicyId)", NULL);
    return(NULL);
  }
  
  return(cur);
}

xmlNodePtr
xmlXadesTmplAddSigPolicyId(xmlNodePtr signaturePolicyId, const xmlChar* identifier, const xmlChar *description, xmlSecTransformId policyDigestMethodId) {
  xmlNodePtr sigPolicyIdNode;
  xmlNodePtr sigPolicyHashNode;
  xmlNodePtr node;
  int ret;
  
  sigPolicyIdNode = xmlSecAddChild(signaturePolicyId, xmlXadesNodeSigPolicyId, xmlXadesDSigNs);
  if (sigPolicyIdNode == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSigPolicyId)", NULL);
    return(NULL);
  }

  node = xmlSecAddChild(sigPolicyIdNode, xmlXadesNodeIdentifier, xmlXadesDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeIdentifier)", NULL);
    xmlFreeNode(sigPolicyIdNode);
    return(NULL);
  }

  ret = xmlSecNodeEncodeAndSetContent(node, identifier);
  if (ret < 0) {
    xmlXadesInternalError("xmlSecNodeEncodeAndSetContent", NULL);
    xmlFreeNode(sigPolicyIdNode);
    xmlFreeNode(node);
    return(NULL);
  }

  node = xmlSecAddChild(sigPolicyIdNode, xmlXadesNodeDescription, xmlXadesDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeDescription)", NULL);
    xmlFreeNode(sigPolicyIdNode);
    return(NULL);
  }

  ret = xmlSecNodeEncodeAndSetContent(node, identifier);
  if (ret < 0) {
    xmlXadesInternalError("xmlSecNodeEncodeAndSetContent", NULL);
    xmlFreeNode(sigPolicyIdNode);
    xmlFreeNode(node);
    return(NULL);
  }

  //add policyHash
  sigPolicyHashNode = xmlSecAddChild(sigPolicyIdNode, xmlXadesNodeSigPolicyHash, xmlXadesDSigNs);
  if (sigPolicyHashNode == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSigPolicyHash)", NULL);
    xmlFreeNode(sigPolicyIdNode);
    return(NULL);
  }
  
  node = xmlSecAddChild(sigPolicyHashNode, xmlSecNodeDigestMethod, xmlXadesDSigNs);
  if (sigPolicyHashNode == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlSecNodeDigestMethod)", NULL);
    xmlUnlinkNode(sigPolicyHashNode);
    xmlFreeNode(sigPolicyHashNode);
    return(NULL);
  }
  if (xmlSetProp(node, xmlSecAttrAlgorithm, policyDigestMethodId->href) == NULL) {
    xmlXadesXmlError2("xmlSetProp", NULL,
                      "name=%s", xmlXadesErrorsSafeString(xmlSecAttrAlgorithm));
    xmlUnlinkNode(sigPolicyHashNode);
    xmlFreeNode(sigPolicyHashNode);
    return(node);
  }

  node = xmlSecAddChild(sigPolicyHashNode, xmlSecNodeDigestValue, xmlXadesDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlSecNodeDigestValue)", NULL);
    xmlUnlinkNode(sigPolicyHashNode);
    xmlFreeNode(sigPolicyHashNode);
    return(NULL);
  }

  return(sigPolicyIdNode);
}

void
xmlXadesTmplAddSignerRole(xmlNodePtr signedSignaturePropertiesNode, const xmlChar* role) {
  xmlNodePtr signerRoleNode;
  xmlNodePtr claimedRolesNode;
  xmlNodePtr claimedRoleNode;
  int ret;

  signerRoleNode = xmlSecAddChild(signedSignaturePropertiesNode, xmlXadesNodeSignerRole, xmlXadesDSigNs);
  if (signerRoleNode == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSignerRole)", NULL);
    return(NULL);
  }

  claimedRolesNode = xmlSecAddChild(signerRoleNode, xmlXadesNodeClaimedRoles, xmlXadesDSigNs);
  if (claimedRolesNode == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeClaimedRoles)", NULL);
    xmlUnlinkNode(signerRoleNode);
    xmlFreeNode(signerRoleNode);
    return(NULL);
  }

  claimedRoleNode = xmlSecAddChild(claimedRolesNode, xmlXadesNodeClaimedRole, xmlXadesDSigNs);
  if (claimedRoleNode == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeClaimedRole)", NULL);
    xmlUnlinkNode(signerRoleNode);
    xmlFreeNode(signerRoleNode);
    return(NULL);
  }

  ret = xmlSecNodeEncodeAndSetContent(claimedRoleNode, role);
  if (ret < 0) {
    xmlXadesInternalError("xmlSecNodeEncodeAndSetContent", NULL);
    xmlUnlinkNode(signerRoleNode);
    xmlFreeNode(signerRoleNode);
    return(NULL);
  }

  return;
}
