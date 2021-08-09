#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Nuevo esquema para modelar segun decreto"""

from datetime import datetime

import pytest

import facho.fe.model as model
import facho.fe.form as form
from facho import fe

import helpers

def simple_invoice():
    invoice = model.Invoice()
    invoice.dian.software_security_code = '12345'
    invoice.dian.software_provider.provider_id = 'provider-id'
    invoice.dian.software_provider.software_id = 'facho'
    invoice.dian.control.prefix = 'SETP'
    invoice.dian.control.from_range =  '1000'
    invoice.dian.control.to_range = '1000'
    invoice.id = '323200000129'
    invoice.issue = datetime.strptime('2019-01-16 10:53:10-05:00', '%Y-%m-%d %H:%M:%S%z')
    invoice.supplier.party.id = '700085371'
    invoice.customer.party.id = '800199436'

    line = invoice.lines.create()
    line.add_tax(model.Taxes.Iva(19.0))

    # TODO(bit4bit) acoplamiento temporal
    # se debe crear primero el subotatl
    # para poder calcularse al cambiar el precio
    line.quantity = 1
    line.price = 1_500_000

    return invoice

def test_simple_invoice_cufe():
    token = '693ff6f2a553c3646a063436fd4dd9ded0311471'
    environment = fe.AMBIENTE_PRODUCCION
    invoice = simple_invoice()
    assert invoice.cufe(token, environment) == '8bb918b19ba22a694f1da11c643b5e9de39adf60311cf179179e9b33381030bcd4c3c3f156c506ed5908f9276f5bd9b4'

def test_simple_invoice_sign_dian(monkeypatch):
    invoice = simple_invoice()

    xmlstring = invoice.to_xml()
    p12_data = open('./tests/example.p12', 'rb').read()
    signer = fe.DianXMLExtensionSigner.from_bytes(p12_data)

    with monkeypatch.context() as m:
        helpers.mock_urlopen(m)
        xmlsigned = signer.sign_xml_string(xmlstring)
    assert "Signature" in xmlsigned


def test_dian_extension_authorization_provider():
    invoice = simple_invoice()
    xml = fe.FeXML.from_string(invoice.to_xml())
    provider_id = xml.get_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:AuthorizationProvider/sts:AuthorizationProviderID')

    assert provider_id.attrib['schemeID'] == '4'
    assert provider_id.attrib['schemeName'] == '31'
    assert provider_id.attrib['schemeAgencyName'] == 'CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)'
    assert provider_id.attrib['schemeAgencyID'] == '195'
    assert provider_id.text == '800197268'
