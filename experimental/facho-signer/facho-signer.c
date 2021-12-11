#include <stdio.h>
#include <stdlib.h>


#include <xmlsec/xmlsec.h>
#include <xmlsec/xmltree.h>
#include <xmlsec/xmldsig.h>
#include <xmlsec/templates.h>
#include <xmlsec/crypto.h>


#define print_error(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__)
#define print_info(fmt, ...) fprintf(stdout, fmt, ##__VA_ARGS__)

const xmlChar ublExtensionDSigNs[] = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2";

char *basename = NULL;

// crea elemento /Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent
xmlNodePtr
xmlFachoTmplUBLExtensionAddExtensionContent(xmlDocPtr doc);

static int
xmlXadesAppInit() {
  xmlInitParser();
  LIBXML_TEST_VERSION;
  
  if ( xmlSecInit() < 0 ) {
    print_error("xmlsec initialization failed.\n");
    return(-1);
  }

  if ( xmlSecCheckVersion() != 1 ) {
    print_error("loaded xmlsec library version is not compatible.\n");
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
    print_error("crypto initialization failed.\n");
    return(-1);
  }

  if ( xmlSecCryptoInit() < 0 ) {
    print_error("xmlsec-crypto initialization failed.\n");
    return(-1);
  }

  return(0);
}

static int
xmlXadesAppShutdown() {

  if ( xmlSecCryptoShutdown() < 0 ) {
    print_error("xmlSecCryptoShutdown failed.\n");
  }

  if ( xmlSecCryptoAppShutdown() < 0 ) {
    print_error("xmlSecCryptoAppShutdown failed.\n");
  }
  
  if ( xmlSecShutdown() < 0 ) {
    print_error("xmlsec shutdown failed.\n");
  }

  xmlCleanupParser();
  return(0);
}

/*    
    X509 *cert = xmlSecOpenSSLKeyDataX509GetCert(keyData, 0);
    if (cert == NULL) {
      print_error("xmlSecOpenSSLKeyDataX509GetKeyCert fail\n");
    }

    char *issuer = X509_NAME_oneline(X509_get_issuer_name(cert), NULL, 0);

    printf("x509 issuer: %s\n", issuer);

    //https://stackoverflow.com/questions/9749560/how-to-calculate-x-509-certificates-sha-1-fingerprint-in-c-c-objective-c
    unsigned char md[EVP_MAX_MD_SIZE];
    unsigned int n;
    const EVP_MD *digest = EVP_get_digestbyname("sha256");
    X509_digest(cert, digest, md, &n);
    printf("%s", "Fingerprint:");
    for(int pos = 0; pos < 19 ; pos++) {
      printf("%02x:", md[pos]);
    }
    printf("%02x\n", md[19]);
*/

static int
xmlXadesSignFile(const char *filename, const char *pkcs12name, const char *password) {
  xmlDocPtr doc = NULL;
  xmlNodePtr signNode = NULL;
  xmlNodePtr refNode = NULL;
  xmlNodePtr keyInfoNode = NULL;
  xmlNodePtr x509DataNode = NULL;
  xmlNodePtr node = NULL;
  xmlSecDSigCtxPtr dsigCtx = NULL;

  int res = -1;
  
  if (filename == NULL) {
   return(-1);
  }

  doc = xmlParseFile(filename);
  if ( (doc == NULL) || (xmlDocGetRootElement(doc) == NULL) ) {
    print_error("error: unable to parse file %s\n", filename);
    goto done;
  }

  signNode = xmlSecTmplSignatureCreate(doc, xmlSecTransformInclC14NId,
                                       xmlSecTransformRsaSha256Id, NULL);
  if ( signNode == NULL ) {
    print_error("error: failed to create signature template.\n");
    goto done;
  }

  xmlAddChild(xmlDocGetRootElement(doc), signNode);

  refNode = xmlSecTmplSignatureAddReference(signNode,
                                            xmlSecTransformSha256Id,
                                            BAD_CAST "xmldsig-facho-ref0", // id
                                            BAD_CAST "", //uri
                                            NULL); //type
  if ( refNode == NULL ) {
    print_error("error: failed to add reference to signature template.\n");
    goto done;
  }
  if ( xmlSecTmplReferenceAddTransform(refNode, xmlSecTransformEnvelopedId) == NULL ) {
    print_error("error: failed to add enveloped transform to reference\n");
    goto done;
  }

  refNode = xmlSecTmplSignatureAddReference(signNode,
                                            xmlSecTransformSha256Id,
                                            BAD_CAST "xmldsig-facho-ref1",
                                            BAD_CAST "#xmldsig-facho-KeyInfo",
                                            NULL);
  if ( refNode == NULL ) {
    print_error("error: failed to add reference to signature template key-info.\n");
    goto done;
  }

  keyInfoNode = xmlSecTmplSignatureEnsureKeyInfo(signNode, BAD_CAST "xmldsig-facho-KeyInfo");
  if ( keyInfoNode == NULL ) {
    print_error("error: failed to add key info.\n");
    goto done;
  }

  x509DataNode = xmlSecTmplKeyInfoAddX509Data(keyInfoNode);
  if ( x509DataNode == NULL ) {
    print_error("error: failde to add x509 DATA \n");
    goto done;
  }

  if ( xmlSecTmplX509DataAddCertificate(x509DataNode) == NULL ) {
    print_error("error: failde to add x509Certificate node\n");
    goto done;
  }

  dsigCtx = xmlSecDSigCtxCreate(NULL);
  if ( dsigCtx == NULL ) {
    print_error("error: dsig context creating failed\n");
    return(-1);
  }
  
  dsigCtx->signKey = xmlSecCryptoAppKeyLoad(pkcs12name,
                                            xmlSecKeyDataFormatPkcs12,
                                            password,
                                            NULL, NULL);
  if ( dsigCtx->signKey == NULL ) {
    print_error("error: failed to load pkcs12\n");
    goto done;
  }

  if ( xmlSecDSigCtxSign(dsigCtx, signNode) < 0 ) {
    print_error("error: signature failed\n");
    goto done;
  }

  node = xmlFachoTmplUBLExtensionAddExtensionContent(doc);
  if ( node == NULL ) {
    print_error("error: failed to add UBLExtensions/UBLExtension/ExtensionContent\n");
    goto done;
  }
  xmlUnlinkNode(signNode);
  xmlSecAddChildNode(node, signNode);

  xmlDocDump(stdout, doc);

  res = 0;

 done:
  if ( dsigCtx != NULL ) {
    xmlSecDSigCtxDestroy(dsigCtx);
  }

  if ( doc != NULL ) {
    xmlFreeDoc(doc);
  }
  return(res);
}

int main(int argc, char *argv[]) {
  basename = argv[0];
  int exitStatus = EXIT_SUCCESS;
  
  if (argc != 4) {
    print_error("%s: <factura.xml> <pc12> <password>\n", basename);
    return(EXIT_FAILURE);
  }

  if ( xmlXadesAppInit() < 0 ) {
    print_error("initialization failed.\n");
    return(EXIT_FAILURE);
  }

  if ( xmlXadesSignFile( argv[1], argv[2], argv[3] ) != 0 ) {
    print_error("%s", "fail to sign file\n");
    exitStatus = EXIT_FAILURE;
  }

  xmlXadesAppShutdown();  
  return(exitStatus);
}



xmlNodePtr
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
      print_error("error: failed to cleate UBLExtensions.\n");
      return(NULL);
    }
  }

  node = xmlSecAddChild(parent, ublExtensionName, ublExtensionDSigNs);
  if ( node == NULL ) {
    print_error("error: failed to add UBLExtension\n");
    xmlFreeNode(parent);
    return(NULL);
  }

  node = xmlSecAddChild(node, extensionContentName, ublExtensionDSigNs);
  if ( node == NULL ) {
    print_error("error: failed to add ExtensionContent");
    return(NULL);
  }

  return(node);
}
