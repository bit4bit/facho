#include <time.h>

#include <libxml/tree.h>
#include "minunit.h"

#include "xades.h"




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
  xmlXadesTmplAddSignedSignatureProperties(node, NULL, &tm);
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

MU_TEST(test_check) {
  mu_check(5 == 7);
}

MU_TEST_SUITE(test_suite) {
  MU_RUN_TEST(test_check);
  MU_RUN_TEST(test_qualifying_properties_layout);
}

int main() {
  MU_RUN_SUITE(test_suite);
  MU_REPORT();
  return MU_EXIT_CODE;
}
