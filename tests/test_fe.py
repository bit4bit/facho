#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import pytest
from facho import fe


def test_xmlsigned_build():
    #openssl req -x509 -sha256 -nodes -subj "/CN=test" -days 1 -newkey rsa:2048 -keyout example.key -out example.pem 
    #openssl pkcs12 -export -out example.p12 -inkey example.key -in example.pem
    signer = fe.DianXMLExtensionSigner('./tests/example.p12')

    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.add_extension(signer)
    xml.attach_extensions()
    elem = xml.find_or_create_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature')
    
    assert elem is not None
    #assert elem.findall('ds:SignedInfo', fe.NAMESPACES) is not None


def test_xmlsigned_with_passphrase_build():
    #openssl req -x509 -sha256 -nodes -subj "/CN=test" -days 1 -newkey rsa:2048 -keyout example.key -out example.pem 
    #openssl pkcs12 -export -out example.p12 -inkey example.key -in example.pem
    signer = fe.DianXMLExtensionSigner('./tests/example-with-passphrase.p12', 'test')

    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.add_extension(signer)
    xml.attach_extensions()
    elem = xml.find_or_create_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature')
    
    assert elem is not None
    #assert elem.findall('ds:SignedInfo', fe.NAMESPACES) is not None


def test_dian_extension_software_security_code():
    security_code = fe.DianXMLExtensionSoftwareSecurityCode('idsoftware', '1234', '1')
    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.add_extension(security_code)
    xml.attach_extensions()
    content = xml.get_element_text('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareSecurityCode')
    assert content is not None
