#include <time.h>

#include "xades.h"

#define xmlXadesAssert2(p, ret) \
  xmlSecAssert2(p, ret)

#define xmlXadesNodeNotFoundError(errorFunction, startNode, targetNodeName, errorObject) \
  xmlSecNodeNotFoundError(errorFunction, startNode, targetNodeName, errorObject)

#define xmlXadesError2(errorFunction, errorObject, msg, param) \
  xmlSecXmlError2(errorFunction, errorObject, msg, param)

#define xmlXadesErrorsSafeString(msg) \
  xmlSecErrorsSafeString(msg)

#define xmlXadesInternalError(errorFunction, errorObject) \
  xmlSecInternalError(errorFunction, errorObject)


xmlNodePtr
xmlXadesTmplQualifyingPropertiesCreateNsPref(xmlDocPtr doc, const xmlChar* id, const xmlChar* nsPrefix) {
  xmlNodePtr qualifyingPropertiesNode;
  xmlNodePtr cur;
  xmlNsPtr ns;

  // crear nodo
  qualifyingPropertiesNode = xmlNewDocNode(doc, NULL, xmlXadesNodeQualifyingProperties, NULL);
  if (qualifyingPropertiesNode == NULL) {
    xmlXadesError2("xmlNewDocNode", NULL, "node=%s", xmlXadesErrorsSafeString(xmlXadesNodeQualifyingProperties));
    return(NULL);
  }

  // crear namespace y asignar
  ns = xmlNewNs(qualifyingPropertiesNode, xmlXadesDSigNs, nsPrefix);
  if (ns == NULL) {
    xmlXadesError2("xmlNewNs", NULL,
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

  return(node);
}
