#ifndef XADES_H
#define XADES_H

#include <libxml/tree.h>

#include <xmlsec/xmltree.h>

#include "xmlsec1/errors_helpers.h"

static const xmlChar xmlXadesNodeQualifyingProperties[] = "QualifyingProperties";
static const xmlChar xmlXadesNodeSignedProperties[] = "SignedProperties";

static const xmlChar xmlXadesNodeSignedSignatureProperties[] = "SignedSignatureProperties";
static const xmlChar xmlXadesNodeSigningTime[] = "SigningTime";

static const xmlChar xmlXadesDSigNs[] = "http://uri.etsi.org/01903/v1.3.2#";

xmlNodePtr
xmlXadesTmplQualifyingPropertiesCreateNsPref(xmlDocPtr doc, const xmlChar* id, const xmlChar* nsPrefix);
xmlNodePtr
xmlXadesTmplAddSignedSignatureProperties(xmlNodePtr parentNode, const xmlChar* id, struct tm* signingTime);
#endif //XADES_H
