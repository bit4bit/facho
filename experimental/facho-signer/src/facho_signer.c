#include "config.h"
#include "xades/xades.h"

#include <xmlsec/xmlsec.h>
#include <xmlsec/xmltree.h>
#include <xmlsec/xmldsig.h>
#include <xmlsec/templates.h>
#include <xmlsec/crypto.h>

#include <stdio.h>
#include <stdlib.h>

#define xmlFachoPrintError(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__)
#define xmlFachoPrintInfo(fmt, ...) fprintf(stdout, fmt, ##__VA_ARGS__)

const xmlChar ublExtensionDSigNs[] = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2";
const xmlChar policyIdDescription[] = "Política de firma para facturas electrónicas de la República de Colombia.";
const xmlChar policyIdIdentifier[] = "https://facturaelectronica.dian.gov.co/politicadefirma/v2/politicadefirmav2.pdf";
  
// crea elemento /Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent
static xmlNodePtr
xmlFachoTmplUBLExtensionAddExtensionContent(xmlDocPtr doc);

// FeC requiere que el digest value del policy identifier sea
// apartir del contenido de la url.
static int
xmlFachoPolicyIdentifierCtxFromFilename(const xmlChar *, xmlSecBufferPtr);


static int
xmlFachoTmplXadesCreate(xmlDocPtr doc, xmlNodePtr signNode) {
  xmlNodePtr qualifyingPropertiesNode = NULL;
  xmlNodePtr signedPropertiesNode = NULL;
  xmlNodePtr signedSignaturePropertiesNode = NULL;
  xmlNodePtr signingCertificateNode = NULL;
  xmlNodePtr signaturePolicyIdentifierNode = NULL;
  xmlNodePtr signaturePolicyIdNode = NULL;
  xmlNodePtr sigPolicyIdNode = NULL;
  xmlNodePtr sigPolicyHashNode = NULL;
  xmlNodePtr signerRoleNode = NULL;
  xmlNodePtr refNode = NULL;
  const xmlChar signedPropertiesId[] = "xmldsig-facho-signed-props";
  const xmlChar signedPropertiesRef[] = "#xmldsig-facho-signed-props";
  
  qualifyingPropertiesNode = xmlXadesTmplQualifyingPropertiesCreate(doc, signNode, BAD_CAST "xades-ref1");
  if (  qualifyingPropertiesNode == NULL ) {
    xmlFachoPrintError("error: failed to add QualifyingProperties node.\n");
    goto fail;
  }

  signedPropertiesNode = xmlXadesTmplAddSignedProperties(qualifyingPropertiesNode, signedPropertiesId);
  if ( signedPropertiesNode == NULL ) {
    xmlFachoPrintError("error: xades failed to add signed properties node.\n");
    goto fail;
  }

  refNode = xmlSecTmplSignatureAddReference(signNode,
                                            xmlSecTransformSha256Id,
                                            BAD_CAST "xmldsig-facho-ref1",
                                            signedPropertiesRef,
                                            BAD_CAST "http://uri.etsi.org/01903#SignedProperties");
  if ( refNode == NULL ) {
    xmlFachoPrintError("error: failed to add reference to signature template xades.\n");
    goto fail;
  }
  if ( xmlSecTmplReferenceAddTransform(refNode, xmlSecTransformInclC14NId) == NULL ) {
    xmlFachoPrintError("error: failed to add enveloped transform to reference for xades\n");
    goto fail;
  }

  const time_t now = time(NULL);
  signedSignaturePropertiesNode = xmlXadesTmplAddSignedSignatureProperties(signedPropertiesNode, localtime(&now));
  if ( signedSignaturePropertiesNode == NULL ) {
    xmlFachoPrintError("error: xades failed to add signed signature properties node.\n");
    goto fail;
  }

  signingCertificateNode = xmlXadesTmplAddSigningCertificate(signedSignaturePropertiesNode, xmlSecTransformSha256Id);
  if ( signingCertificateNode == NULL ) {
    xmlFachoPrintError("error: failed to add SigningCertificate node \n");
    goto fail;
  }

  signaturePolicyIdentifierNode = xmlXadesTmplAddSignaturePolicyIdentifier(signedSignaturePropertiesNode);
  if ( signaturePolicyIdentifierNode == NULL ) {
    xmlFachoPrintError("error: failed to add PolicyIdentifier node\n");
    goto fail;
  }

  signaturePolicyIdNode = xmlXadesTmplAddSignaturePolicyId(signaturePolicyIdentifierNode);
  if ( signaturePolicyIdNode == NULL ) {
    xmlFachoPrintError("error: failed to add SignaturePolicyId node.\n");
    goto fail;
  }

  sigPolicyIdNode = xmlXadesTmplAddSigPolicyId(signaturePolicyIdNode, policyIdIdentifier, policyIdDescription);
  if ( sigPolicyIdNode == NULL ) {
    xmlFachoPrintError("error: failed to add SigPolicyId node.\n");
    goto fail;
  }

  sigPolicyHashNode = xmlXadesTmplAddSigPolicyHash(signaturePolicyIdNode, xmlSecTransformSha256Id);
  if ( sigPolicyHashNode == NULL ) {
    xmlFachoPrintError("error: failed to add SigPolicyHash node.\n");
    goto fail;
  }

  signerRoleNode = xmlXadesTmplAddSignerRole(signedSignaturePropertiesNode, BAD_CAST "supplier");
  if ( signerRoleNode == NULL ) {
    xmlFachoPrintError("error: failed to add SignerRole node.\n");
    goto fail;
  }

  
  return(0);
 fail:
  xmlUnlinkNode(qualifyingPropertiesNode);
  xmlFreeNode(qualifyingPropertiesNode);
  return(-1);
}

int
xmlFachoInit() {
  xmlInitParser();
  LIBXML_TEST_VERSION;
  
  if ( xmlSecInit() < 0 ) {
    xmlFachoPrintError("xmlsec initialization failed.\n");
    return(-1);
  }

  if ( xmlSecCheckVersion() != 1 ) {
    xmlFachoPrintError("loaded xmlsec library version is not compatible.\n");
    return(-1);
  }

#ifdef XMLSEC_CRYPTO_DYNAMIC_LOADING
    if(xmlSecCryptoDLLoadLibrary( NULL ) < 0) {
        fprintf(stderr, "Error: unable to load default xmlsec-crypto library. Make sure\n"
                        "that you have it installed and check shared libraries path\n"
                        "(LD_LIBRARY_PATH and/or LTDL_LIBRARY_PATH) environment variables.\n");
        return(-1);     
    }
#endif /* XMLSEC_CRYPTO_DYNAMIC_LOADING */
   
  if ( xmlSecCryptoAppInit(NULL) < 0 ) {
    xmlFachoPrintError("crypto initialization failed.\n");
    return(-1);
  }

  if ( xmlSecCryptoInit() < 0 ) {
    xmlFachoPrintError("xmlsec-crypto initialization failed.\n");
    return(-1);
  }

  return(0);
}

int
xmlFachoShutdown() {

  if ( xmlSecCryptoShutdown() < 0 ) {
    xmlFachoPrintError("xmlSecCryptoShutdown failed.\n");
  }

  if ( xmlSecCryptoAppShutdown() < 0 ) {
    xmlFachoPrintError("xmlSecCryptoAppShutdown failed.\n");
  }
  
  if ( xmlSecShutdown() < 0 ) {
    xmlFachoPrintError("xmlsec shutdown failed.\n");
  }

  xmlCleanupParser();
  return(0);
}

int
xmlFachoSignFile(FILE *out, const char *filename, const char *pkcs12name, const char *password) {
  xmlDocPtr doc = NULL;
  xmlNodePtr signNode = NULL;
  xmlNodePtr refNode = NULL;
  xmlNodePtr keyInfoNode = NULL;
  xmlNodePtr x509DataNode = NULL;
  xmlNodePtr node = NULL;
  xmlSecDSigCtxPtr dsigCtx = NULL;
  xmlXadesDSigCtxPtr xadesDsigCtx = NULL;

  int res = -1;
  
  if (filename == NULL) {
   return(-1);
  }

  doc = xmlParseFile(filename);
  if ( (doc == NULL) || (xmlDocGetRootElement(doc) == NULL) ) {
    xmlFachoPrintError("error: unable to parse file %s\n", filename);
    goto done;
  }

  signNode = xmlSecTmplSignatureCreate(doc, xmlSecTransformInclC14NId,
                                       xmlSecTransformRsaSha256Id, NULL);
  if ( signNode == NULL ) {
    xmlFachoPrintError("error: failed to create signature template.\n");
    goto done;
  }

  xmlAddChild(xmlDocGetRootElement(doc), signNode);

  refNode = xmlSecTmplSignatureAddReference(signNode,
                                            xmlSecTransformSha256Id,
                                            BAD_CAST "xmldsig-facho-ref0", // id
                                            BAD_CAST "", //uri
                                            NULL); //type
  if ( refNode == NULL ) {
    xmlFachoPrintError("error: failed to add reference to signature template.\n");
    goto done;
  }
  if ( xmlSecTmplReferenceAddTransform(refNode, xmlSecTransformEnvelopedId) == NULL ) {
    xmlFachoPrintError("error: failed to add enveloped transform to reference\n");
    goto done;
  }

  refNode = xmlSecTmplSignatureAddReference(signNode,
                                            xmlSecTransformSha256Id,
                                            BAD_CAST "xmldsig-facho-ref2",
                                            BAD_CAST "#xmldsig-facho-KeyInfo",
                                            NULL);
  if ( refNode == NULL ) {
    xmlFachoPrintError("error: failed to add reference to signature template key-info.\n");
    goto done;
  }

  keyInfoNode = xmlSecTmplSignatureEnsureKeyInfo(signNode, BAD_CAST "xmldsig-facho-KeyInfo");
  if ( keyInfoNode == NULL ) {
    xmlFachoPrintError("error: failed to add key info.\n");
    goto done;
  }

  x509DataNode = xmlSecTmplKeyInfoAddX509Data(keyInfoNode);
  if ( x509DataNode == NULL ) {
    xmlFachoPrintError("error: failde to add x509 DATA \n");
    goto done;
  }

  if ( xmlSecTmplX509DataAddCertificate(x509DataNode) == NULL ) {
    xmlFachoPrintError("error: failde to add x509Certificate node\n");
    goto done;
  }


  if ( xmlFachoTmplXadesCreate(doc, signNode) < 0 ){
    xmlFachoPrintError("error: xmlFachoTmplXadesCreate failed.\n");
    goto done;
  }

  dsigCtx = xmlSecDSigCtxCreate(NULL);
  if ( dsigCtx == NULL ) {
    xmlFachoPrintError("error: dsig context creating failed\n");
    return(-1);
  }

  // cargamos el archivo pkcs12 con llave privado y certificados x509
  dsigCtx->signKey = xmlSecCryptoAppKeyLoad(pkcs12name,
                                            xmlSecKeyDataFormatPkcs12,
                                            password,
                                            NULL, NULL);
  if ( dsigCtx->signKey == NULL ) {
    xmlFachoPrintError("error: failed to load pkcs12\n");
    goto done;
  }

  xmlXadesPolicyIdentifierCtx policyIdCtx;

  // por ahora el hash del identificador lo tomamos del pdf de la dian
  policyIdCtx.contentCallback = &xmlFachoPolicyIdentifierCtxFromFilename;
    
  xadesDsigCtx = xmlXadesDSigCtxCreate(dsigCtx, XADES_DIGEST_SHA256, &policyIdCtx);
  if ( xadesDsigCtx == NULL ) {
    xmlFachoPrintError("error: xades context creating failed.\n");
    return(-1);
  }

  // debe existir el elemento antes del firmado
  node = xmlFachoTmplUBLExtensionAddExtensionContent(doc);
  if ( node == NULL ) {
    xmlFachoPrintError("error: failed to add UBLExtensions/UBLExtension/ExtensionContent\n");
    goto done;
  }


  // realizar firma de documento
  if ( xmlXadesDSigCtxSign(xadesDsigCtx, signNode) < 0 ) {
    xmlFachoPrintError("error: signature failed\n");
    goto done;
  }


  xmlUnlinkNode(signNode);
  xmlSecAddChildNode(node, signNode);

  xmlDocDump(out, doc);

  res = 0;

 done:
  if ( xadesDsigCtx != NULL ) {
    xmlXadesDSigCtxDestroy(xadesDsigCtx);
  }

  if ( dsigCtx != NULL ) {
    xmlSecDSigCtxDestroy(dsigCtx);
  }

  if ( doc != NULL ) {
    xmlFreeDoc(doc);
  }
  return(res);
}

static xmlNodePtr
xmlFachoTmplUBLExtensionAddExtensionContent(xmlDocPtr doc) {
  xmlNodePtr node = NULL;
  xmlNodePtr parent = NULL;
  const xmlChar ublExtensionsName[] = "UBLExtensions";
  const xmlChar ublExtensionName[] = "UBLExtension";
  const xmlChar extensionContentName[] = "ExtensionContent";
    
  parent = xmlSecFindNode(xmlDocGetRootElement(doc), ublExtensionsName, ublExtensionDSigNs);
  if ( parent == NULL ) {
    parent = xmlSecAddChild(xmlDocGetRootElement(doc), ublExtensionsName,  ublExtensionDSigNs);
    if ( parent == NULL ) {
      xmlFachoPrintError("error: failed to cleate UBLExtensions.\n");
      return(NULL);
    }
  }

  // adicionamos nuevo elemento UBLExtension
  node = xmlSecAddChild(parent, ublExtensionName, ublExtensionDSigNs);
  if ( node == NULL ) {
    xmlFachoPrintError("error: failed to add UBLExtension\n");
    xmlFreeNode(parent);
    return(NULL);
  }

  // adicionamos nuevo elemento ExtensionContent
  node = xmlSecAddChild(node, extensionContentName, ublExtensionDSigNs);
  if ( node == NULL ) {
    xmlFachoPrintError("error: failed to add ExtensionContent");
    return(NULL);
  }

  return(node);
}

static int
xmlFachoPolicyIdentifierCtxFromFilename(const xmlChar *policyId, xmlSecBufferPtr buffer) {
  static unsigned char politicafirmav2[] = {
    /**
     * generado con https://github.com/Jamesits/bin2array
     */
#include "politicafirmav2.c"
  };

  return xmlSecBufferAppend(buffer, politicafirmav2, sizeof(politicafirmav2));
}
