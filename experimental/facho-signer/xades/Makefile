.PHONY: test

CC=gcc

test: xmlsec1/errors.c xmlsec1/xmltree.c templates.c xades_test.c
	$(CC) -o $@ -Wall -Werror -std=gnu11 $(shell pkg-config libxml-2.0 --cflags --libs) $(shell pkg-config xmlsec1 --cflags --libs) $^ 
	./test
