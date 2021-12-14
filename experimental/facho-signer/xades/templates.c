#include "xades.h"

#include <xmlsec/templates.h>

#include <time.h>
#include <string.h>


static xmlNodePtr
xmlXadesTmplAddDigest(xmlNodePtr parentNode, const xmlChar *digestMethod, const xmlChar *digestValue);

xmlNodePtr
xmlXadesAddChildRecursiveNs(xmlNodePtr startNode, const xmlChar* path, const xmlChar* nsPrefix) {
  char *curToken;
  char* cpath = strdup((char *)path);
  char* savePtr;
  xmlNodePtr curNode = NULL;
  xmlNodePtr parentNode = startNode;


  curToken = strtok_r(cpath, "/", &savePtr);
  while(curToken != NULL) {
    curNode = xmlSecFindChild(parentNode, BAD_CAST curToken, nsPrefix);
    if (curNode == NULL) {
      curNode = xmlSecAddChild(parentNode, BAD_CAST curToken, nsPrefix);
      if (curNode == NULL) {
        xmlXadesInternalError("xmlSecAddChild(%s)", curToken);
        return(NULL);
      }
    }

    parentNode = curNode;

    curToken = strtok_r(NULL, "/", &savePtr);
  }

  free(cpath);
  return(curNode);
}

xmlNodePtr
xmlXadesTmplQualifyingPropertiesCreate(xmlDocPtr doc, xmlNodePtr signatureNode, const xmlChar *id) {
  xmlNodePtr objectNode;
  xmlNodePtr qualifyingPropertiesNode;

  xmlNewGlobalNs(doc, xmlXadesDSigNs, BAD_CAST "xades");

  objectNode = xmlSecTmplSignatureAddObject(signatureNode, NULL, NULL, NULL);
  if (objectNode == NULL) {
    xmlXadesInternalError("xmlSecTmplSignatureAddObject(signatureNode)", NULL);
    return(NULL);
  }

  qualifyingPropertiesNode = xmlSecAddChild(objectNode, xmlXadesNodeQualifyingProperties, xmlXadesDSigNs);
  if (qualifyingPropertiesNode == NULL) {
    xmlXadesXmlError2("xmlNewDocNode", NULL, "node=%s", xmlXadesErrorsSafeString(xmlXadesNodeQualifyingProperties));
    return(NULL);
  }

  if (id != NULL) {
    xmlSetProp(qualifyingPropertiesNode, BAD_CAST "Id", id);
  }

  return(qualifyingPropertiesNode);
}

xmlNodePtr
xmlXadesTmplQualifyingPropertiesCreateNsPref(xmlDocPtr doc, const xmlChar* id, const xmlChar* nsPrefix) {
  xmlNodePtr qualifyingPropertiesNode;
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
    xmlSetProp(qualifyingPropertiesNode, BAD_CAST "Id", id);
  }

 
  return (qualifyingPropertiesNode);
}

xmlNodePtr
xmlXadesTmplAddSignedProperties(xmlNodePtr qualifyingPropertiesNode, const xmlChar* id) {
  xmlNodePtr cur;

  xmlXadesAssert2(qualifyingPropertiesNode != NULL, NULL);
  
  cur = xmlSecAddChild(qualifyingPropertiesNode, xmlXadesNodeSignedProperties, xmlXadesDSigNs);
  if (cur == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSignedProperties)", NULL);
    return(NULL);
  }

  if (id != NULL) {
    xmlSetProp(cur, BAD_CAST "Id", id);
  }

  return(cur);
}

xmlNodePtr
xmlXadesTmplAddSignedSignatureProperties(xmlNodePtr signedPropertiesNode, struct tm* signingTime) {
  xmlNodePtr cur;
  xmlNodePtr node;

  xmlXadesAssert2(signedPropertiesNode != NULL, NULL);
  
  // add SignedSignatureProperties
  node = xmlSecAddChild(signedPropertiesNode, xmlXadesNodeSignedSignatureProperties, xmlXadesDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSignedSignatureProperties)", NULL);
    return(NULL);
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

  return(node);
}

xmlNodePtr
xmlXadesTmplAddSigningCertificate(xmlNodePtr signedSignaturePropertiesNode, xmlSecTransformId digestMethodId) {
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
xmlXadesTmplAddCert(xmlNodePtr signingCertificateNode) {
  xmlNodePtr certNode;

  xmlXadesAssert2(signingCertificateNode != NULL, NULL);

  certNode = xmlSecAddChild(signingCertificateNode, xmlXadesNodeCert, xmlXadesDSigNs);
  if (certNode == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeCert)", NULL);
    return(NULL);
  }

  return(certNode);
}

xmlNodePtr
xmlXadesTmplAddCertDigest(xmlNodePtr certNode, const xmlChar *digestMethod, const xmlChar *digestValue) {
  xmlNodePtr node;

  xmlXadesAssert2(certNode != NULL, NULL);

  node = xmlSecAddChild(certNode, xmlXadesNodeCertDigest, xmlXadesDSigNs);
  if ( node == NULL ) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeCertDigest)", NULL);
    return(NULL);
  }

  if ( xmlXadesTmplAddDigest(node, digestMethod, digestValue) == NULL) {
    xmlXadesInternalError("xmlXadesTmplAddDigest(node, digestMethodId)", NULL);
    return(NULL);
  }

  return(certNode);
}

xmlNodePtr
xmlXadesTmplAddSignaturePolicyIdentifier(xmlNodePtr signedSignaturePropertiesNode) {
  xmlNodePtr cur;

  xmlXadesAssert2(signedSignaturePropertiesNode != NULL, NULL);

  cur = xmlSecAddChild(signedSignaturePropertiesNode, xmlXadesNodeSignaturePolicyIdentifier, xmlXadesDSigNs);
  if (cur == NULL) {
    xmlXadesInternalError("xmlsecAddChild(xmlXadesNodeSignaturePolicyIdentifier)", NULL);
    return(NULL);
  }

  return(cur);
}

xmlNodePtr
xmlXadesTmplAddSignaturePolicyId(xmlNodePtr signaturePolicyIdentifierNode) {
  xmlNodePtr cur;

  xmlXadesAssert2(signaturePolicyIdentifierNode != NULL, NULL);

  cur = xmlSecAddChild(signaturePolicyIdentifierNode, xmlXadesNodeSignaturePolicyId, xmlXadesDSigNs);
  if (cur == NULL) {
    xmlXadesInternalError("xmlsecAddChild(cur)", NULL);
    return(NULL);
  }

  return(cur);
}

xmlNodePtr
xmlXadesTmplAddSigPolicyId(xmlNodePtr signaturePolicyId, const xmlChar* identifier, const xmlChar *description) {
  xmlNodePtr sigPolicyIdNode;
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

  ret = xmlSecNodeEncodeAndSetContent(node, description);
  if (ret < 0) {
    xmlXadesInternalError("xmlSecNodeEncodeAndSetContent", NULL);
    xmlFreeNode(sigPolicyIdNode);
    xmlFreeNode(node);
    return(NULL);
  }

  return(sigPolicyIdNode);
}

xmlNodePtr
xmlXadesTmplAddSigPolicyHash(xmlNodePtr parentNode, xmlSecTransformId digestMethodId) {
  xmlNodePtr node;
  xmlXadesAssert2(parentNode != NULL, NULL);

  //add policyHash
  node = xmlSecAddChild(parentNode, xmlXadesNodeSigPolicyHash, xmlXadesDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeSigPolicyHash)", NULL);
    return(NULL);
  }

  if ( xmlXadesTmplAddDigest(node, digestMethodId->href, BAD_CAST "") == NULL) {
    xmlXadesInternalError("xmlXadesTmplAddDigest(node, digestMethodId)", NULL);
    return(NULL);
  }

  return node;
}

// MACHETE(bit4bit) como usar SecTransform para almacenar el digest
static xmlNodePtr
xmlXadesTmplAddDigest(xmlNodePtr parentNode, const xmlChar *digestMethod, const xmlChar *digestValue) {
  xmlNodePtr node;
  
  xmlXadesAssert2(parentNode != NULL, NULL);

  node = xmlSecAddChild(parentNode, xmlSecNodeDigestMethod, xmlSecDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlSecNodeDigestMethod)", NULL);
    return(NULL);
  }
  if (xmlSetProp(node, xmlSecAttrAlgorithm, digestMethod) == NULL) {
    xmlXadesXmlError2("xmlSetProp", NULL,
                      "name=%s", xmlXadesErrorsSafeString(xmlSecAttrAlgorithm));
    xmlUnlinkNode(node);
    xmlFreeNode(node);
    return(NULL);
  }

  node = xmlSecAddChild(parentNode, xmlSecNodeDigestValue, xmlSecDSigNs);
  if (node == NULL) {
    xmlXadesInternalError("xmlSecAddChild(xmlSecNodeDigestValue)", NULL);
    return(NULL);
  }

  if (xmlSecNodeEncodeAndSetContent(node, digestValue) < 0) {
    xmlXadesInternalError("xmlSecNodeEncodeAndSetContent", NULL);
    return(NULL);
  }

  return parentNode;
}

xmlNodePtr
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

  return(signerRoleNode);
}


xmlNodePtr
xmlXadesTmplAddIssuerSerial(xmlNodePtr certNode, const xmlChar *issuerName, const xmlChar *issuerNumber) {
  xmlNodePtr issuerSerialNode;
  xmlNodePtr node;

  xmlXadesAssert2(certNode != NULL, NULL);

  issuerSerialNode = xmlSecAddChild(certNode, xmlXadesNodeIssuerSerial, xmlXadesDSigNs);
  if ( issuerSerialNode == NULL ) {
    xmlXadesInternalError("xmlSecAddChild(certNode, xmlXadesIssuerSerial)", NULL);
    return(NULL);
  }

  node = xmlSecAddChild(issuerSerialNode, xmlXadesNodeX509IssuerName, xmlSecDSigNs);
  if ( node == NULL ) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeX509IssuerName)", NULL);
    xmlFreeNode(issuerSerialNode);
    return(NULL);
  }

  if (xmlSecNodeEncodeAndSetContent(node, issuerName) < 0) {
    xmlXadesInternalError("xmlSecNodeEncodeAndSetContent", NULL);
    xmlUnlinkNode(issuerSerialNode);
    xmlFreeNode(issuerSerialNode);
    return(NULL);
  }

  node = xmlSecAddChild(issuerSerialNode, xmlXadesNodeX509IssuerNumber, xmlSecDSigNs);
  if ( node == NULL ) {
    xmlXadesInternalError("xmlSecAddChild(xmlXadesNodeX509IssuerNumber)", NULL);
    xmlFreeNode(issuerSerialNode);
    return(NULL);
  }

  if (xmlSecNodeEncodeAndSetContent(node, issuerNumber) < 0) {
    xmlXadesInternalError("xmlSecNodeEncodeAndSetContent", NULL);
    xmlUnlinkNode(issuerSerialNode);
    xmlFreeNode(issuerSerialNode);
    return(NULL);
  }

  return(issuerSerialNode);
}
