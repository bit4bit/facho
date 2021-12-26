/**
 * This file is part of facho.  The COPYRIGHT file at the top level of
 * this repository contains the full copyright notices and license terms.
 */

#ifndef FACHO_SIGNER_H
#define FACHO_SIGNER_H

#include <stdio.h>

int
xmlFachoInit();

int
xmlFachoShutdown();

int
xmlFachoSignFile(FILE *out, const char *filename, const char *pkcs12name, const char *password);

#endif /* FACHO_SIGNER_H */
