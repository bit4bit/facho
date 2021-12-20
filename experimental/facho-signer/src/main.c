#include "xades/xades.h"
#include "facho_signer.h"

#include <stdio.h>
#include <stdlib.h>


static char *basename = NULL;

int main(int argc, char *argv[]) {
  int exitStatus = EXIT_SUCCESS;

  basename = argv[0];
  
  if (argc != 4) {
    fprintf(stderr, "%s: <factura.xml> <pc12> <password>\n", basename);
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
