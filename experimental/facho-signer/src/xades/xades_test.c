/**
 * This file is part of facho.  The COPYRIGHT file at the top level of
 * this repository contains the full copyright notices and license terms.
 */

#include <time.h>

#include <libxml/tree.h>
#include "minunit.h"

#include "xades.h"


MU_TEST(test_xml_add_node_recursive) {
  xmlDocPtr doc;
  xmlNodePtr root;
  xmlNodePtr child;
  xmlChar* xmlbuff;
  int xmlbuffsize;
  
  doc = xmlNewDoc(BAD_CAST "1.0");
  root = xmlNewNode(NULL, BAD_CAST "root");
  xmlDocSetRootElement(doc, root);

  child = xmlXadesAddChildRecursiveNs(root, BAD_CAST "A/B/C", NULL);
  mu_check(child != NULL);

  xmlDocDumpMemory(doc, &xmlbuff, &xmlbuffsize);
  mu_assert_string_eq("<?xml version=\"1.0\"?>\n"
                      "<root>\n"
                      "<A>\n"
                      "<B>\n"
                      "<C/>\n"
                      "</B>\n"
                      "</A>\n"
                      "</root>\n"
                      , (char *)xmlbuff);
}

MU_TEST(test_qualifying_properties_layout) {
  xmlDocPtr doc;
  xmlNodePtr root;
  xmlNodePtr node;
  xmlChar* xmlbuff;
  int buffersize;
  struct tm tm;

  memset(&tm, 0, sizeof(tm));
  tm.tm_year = 2021 - 1900;
  tm.tm_mon = 11;
  tm.tm_mday = 6;
  tm.tm_hour = 12;
  tm.tm_min = 0;
  tm.tm_sec = 50;


  doc = xmlNewDoc(BAD_CAST "1.0");
  root = xmlNewNode(NULL, BAD_CAST "root");
  xmlDocSetRootElement(doc, root);
  
  node = xmlXadesTmplQualifyingPropertiesCreateNsPref(doc, BAD_CAST "123", NULL);
  xmlXadesTmplAddSignedSignatureProperties(node, &tm);
  mu_check(node != NULL);
  
  xmlSecAddChildNode(root, node);
  xmlDocDumpMemory(doc, &xmlbuff, &buffersize);

  // bit4bit: no se como pasar el namespace al root
  mu_assert_string_eq("<?xml version=\"1.0\"?>\n"
                      "<root>\n"
                      "<QualifyingProperties xmlns=\"http://uri.etsi.org/01903/v1.3.2#\" id=\"123\">\n"
                      "<SignedProperties>\n"
                      "<SignedSignatureProperties>\n"
                      "<SigningTime>2021-12-06T12:00:50</SigningTime>\n"
                      "</SignedSignatureProperties>\n"
                      "</SignedProperties>\n"
                      "</QualifyingProperties>\n"
                      "</root>\n"
                      , (char *)xmlbuff);
  
  xmlFree(xmlbuff);
  xmlFreeDoc(doc);
}

MU_TEST_SUITE(test_suite) {
  MU_RUN_TEST(test_xml_add_node_recursive);
  MU_RUN_TEST(test_qualifying_properties_layout);
}

int main() {
  MU_RUN_SUITE(test_suite);
  MU_REPORT();
  return MU_EXIT_CODE;
}
