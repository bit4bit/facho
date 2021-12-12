.PHONY: facho-signer

CC = gcc

CFLAGS = -Wall -Werror -std=gnu11
CFLAGS += $(shell pkg-config libxml-2.0 --cflags)
CFLAGS += $(shell pkg-config xmlsec1 --cflags)
CFLAGS += $(shell pkg-config xmlsec1-openssl --cflags)
CFLAGS += -Ixades

LDFLAGS = $(shell pkg-config libxml-2.0 --libs)
LDFLAGS += $(shell pkg-config xmlsec1 --libs)
LDFLAGS += $(shell pkg-config xmlsec1-openssl --libs)
LDFLAGS += xades/templates.c xades/xades.c 

facho-signer: crypto.c facho-signer.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $^ 
