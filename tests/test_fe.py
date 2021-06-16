#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import datetime

import pytest
from facho import fe


import helpers


def test_xmlsigned_build(monkeypatch):
    #openssl req -x509 -sha256 -nodes -subj "/CN=test" -days 1 -newkey rsa:2048 -keyout example.key -out example.pem
    #openssl pkcs12 -export -out example.p12 -inkey example.key -in example.pem
    signer = fe.DianXMLExtensionSigner('./tests/example.p12')

    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')


    with monkeypatch.context() as m:
        helpers.mock_urlopen(m)
        signer.sign_xml_element(xml.root)

    elem = xml.find_or_create_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature')

    assert elem is not None
    #assert elem.findall('ds:SignedInfo', fe.NAMESPACES) is not None


def test_xmlsigned_with_passphrase_build(monkeypatch):
    #openssl req -x509 -sha256 -nodes -subj "/CN=test" -days 1 -newkey rsa:2048 -keyout example.key -out example.pem
    #openssl pkcs12 -export -out example.p12 -inkey example.key -in example.pem
    signer = fe.DianXMLExtensionSigner('./tests/example-with-passphrase.p12', 'test')

    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')

    with monkeypatch.context() as m:
        helpers.mock_urlopen(m)
        signer.sign_xml_element(xml.root)

    elem = xml.find_or_create_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature')

    assert elem is not None
    #assert elem.findall('ds:SignedInfo', fe.NAMESPACES) is not None


def test_dian_extension_software_security_code():
    security_code = fe.DianXMLExtensionSoftwareSecurityCode('idsoftware', '1234', '1')
    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.add_extension(security_code)
    content = xml.get_element_text('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareSecurityCode')
    assert content is not None

def test_dian_extension_invoice_authorization():
    invoice_authorization = '18762002346472'
    inv_auth_ext = fe.DianXMLExtensionInvoiceAuthorization(invoice_authorization,
                                                           datetime(2017, 2, 23),
                                                           datetime(2019, 8, 23),
                                                           'MD', 100001, 174999)
    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.add_extension(inv_auth_ext)
    auth = xml.get_element_text('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceControl/sts:InvoiceAuthorization')
    assert auth == invoice_authorization

def test_dian_extension_software_provider():
    nit = '123456789'
    id_software = 'ABCDASDF123'
    software_provider_extension = fe.DianXMLExtensionSoftwareProvider(nit, '', id_software)

    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.add_extension(software_provider_extension)

    give_nit = xml.get_element_text('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareProvider/sts:ProviderID')
    assert nit == give_nit

def test_dian_extension_authorization_provider():
    auth_provider_extension = fe.DianXMLExtensionAuthorizationProvider()
    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.add_extension(auth_provider_extension)
    dian_nit = xml.get_element_text('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:AuthorizationProvider/sts:AuthorizationProviderID')
    assert dian_nit == '800197268'

def test_dian_invoice_without_namespace_in_root():
    xml = fe.FeXML('Invoice',
                   'http://www.dian.gov.co/contratos/facturaelectronica/v1')

    assert "<Invoice" in xml.tostring()


def test_xml_sign_dian(monkeypatch):
    xml = fe.FeXML('Invoice',
                'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.find_or_create_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')
    ublextension = xml.fragment('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension', append=True)
    extcontent = ublextension.find_or_create_element('/ext:UBLExtension/ext:ExtensionContent')

    xmlstring = xml.tostring()
    print(xmlstring)
    signer = fe.DianXMLExtensionSigner('./tests/example.p12')

    with monkeypatch.context() as m:
        helpers.mock_urlopen(m)
        xmlsigned = signer.sign_xml_string(xmlstring)
    assert "Signature" in xmlsigned

def test_xml_sign_dian_using_bytes(monkeypatch):
    xml = fe.FeXML('Invoice',
                'http://www.dian.gov.co/contratos/facturaelectronica/v1')
    xml.find_or_create_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')
    ublextension = xml.fragment('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension', append=True)
    extcontent = ublextension.find_or_create_element('/ext:UBLExtension/ext:ExtensionContent')

    xmlstring = xml.tostring()
    p12_data = open('./tests/example.p12', 'rb').read()
    signer = fe.DianXMLExtensionSigner.from_bytes(p12_data)

    with monkeypatch.context() as m:
        helpers.mock_urlopen(m)
        xmlsigned = signer.sign_xml_string(xmlstring)
    assert "Signature" in xmlsigned
