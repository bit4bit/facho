/**
 * This file is part of facho.  The COPYRIGHT file at the top level of
 * this repository contains the full copyright notices and license terms.
 */

#include "xades/xades.h"
#include "facho_signer.h"

#include <stdio.h>
#include <stdlib.h>


static char *basename = NULL;

void usage(FILE *out);

int main(int argc, char *argv[]) {
  int exitStatus = EXIT_SUCCESS;
  basename = argv[0];
  
  if (argc != 4) {
    usage(stderr);
    return(EXIT_FAILURE);
  }

  if ( xmlFachoInit() < 0 ) {
    fprintf(stderr, "initialization failed.\n");
    return(EXIT_FAILURE);
  }

  if ( xmlFachoSignFile( stdout, argv[1], argv[2], argv[3] ) != 0 ) {
    fprintf(stderr, "fail to sign file\n");
    exitStatus = EXIT_FAILURE;
  }

  xmlFachoShutdown();  
  return(exitStatus);
}

void
usage(FILE *out) {
  fprintf(out, "%s: <factura.xml> <pc12> <password>\n", basename);
  fprintf(out, "%s", "Firmado electronico para facturacion en Colombia.\n"
          "Segun el documento (Anexo Técnico de Factura Electrónica de Venta – Versión 1.7.-2020).\n"
          "A considerar:\n" \
          " * adiciona un nuevo elemento //ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent\n");
}
