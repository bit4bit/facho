#ifndef XADES_H
#define XADES_H

#include <libxml/tree.h>

#include <xmlsec/xmltree.h>
#include <xmlsec/transforms.h>

#include "xmlsec1/errors_helpers.h"

static const xmlChar xmlXadesNodeQualifyingProperties[] = "QualifyingProperties";
static const xmlChar xmlXadesNodeSignedProperties[] = "SignedProperties";

static const xmlChar xmlXadesNodeSignedSignatureProperties[] = "SignedSignatureProperties";
static const xmlChar xmlXadesNodeSigningTime[] = "SigningTime";
static const xmlChar xmlXadesNodeSigningCertificate[] = "SigningCertificate";
static const xmlChar xmlXadesNodeCertificate[] = "Cert";
static const xmlChar xmlXadesNodeSignaturePolicyIdentifier[] = "SignaturePolicyIdentifier";
static const xmlChar xmlXadesNodeSignaturePolicyId[] = "SignaturePolicyId";
static const xmlChar xmlXadesNodeSigPolicyId[] = "SignaturePolicyId";
static const xmlChar xmlXadesNodeIdentifier[] = "Identifier";
static const xmlChar xmlXadesNodeDescription[] = "Description";
static const xmlChar xmlXadesNodeSigPolicyHash[] = "SigPolicyHash";

static const xmlChar xmlXadesNodeSignerRole[] = "SignerRole";
static const xmlChar xmlXadesNodeClaimedRoles[] = "ClaimedRoles";
static const xmlChar xmlXadesNodeClaimedRole[] = "ClaimedRole";

static const xmlChar xmlXadesDSigNs[] = "http://uri.etsi.org/01903/v1.3.2#";

xmlNodePtr
xmlXadesTmplQualifyingPropertiesCreateNsPref(xmlDocPtr doc, const xmlChar* id, const xmlChar* nsPrefix);


xmlNodePtr
xmlXadesTmplAddSignedSignatureProperties(xmlNodePtr parentNode, const xmlChar* id, struct tm* signingTime);

xmlNodePtr
xmlXadesTmplAddSigningCertificate(xmlNodePtr parentNode);
xmlNodePtr
xmlXadesTmplAddCert(xmlNodePtr signingCertificateNode);
xmlNodePtr
xmlXadesTmplAddSignaturePolicyIdentifierSignaturePolicyId(xmlNodePtr signedSignaturePropertiesNode);

#endif //XADES_H
