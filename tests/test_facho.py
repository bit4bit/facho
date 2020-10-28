#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest

#from click.testing import CliRunner

from facho import facho
#from facho import cli


def test_facho_xml():
    xml = facho.FachoXML('root')
    invoice = xml.find_or_create_element('/root/Invoice')
    assert xml.tostring() == '<root><Invoice/></root>'
    invoice.text = 'Test'
    assert xml.tostring() == '<root><Invoice>Test</Invoice></root>'

    invoice_line = xml.find_or_create_element('/root/Invoice/Line')
    assert xml.tostring() == '<root><Invoice>Test<Line/></Invoice></root>'


def test_facho_xml_with_attr():
    xml = facho.FachoXML('root')
    invoice = xml.find_or_create_element('/root/Invoice[id=123]')
    assert xml.tostring() == '<root><Invoice id="123"/></root>'

def test_facho_xml_idempotent():
    xml = facho.FachoXML('root')
    invoice = xml.find_or_create_element('/root/Invoice')
    assert xml.tostring() == '<root><Invoice/></root>'

    xml.find_or_create_element('/root/Invoice')
    assert xml.tostring() == '<root><Invoice/></root>'

    xml.find_or_create_element('/root/Invoice')
    assert xml.tostring() == '<root><Invoice/></root>'

    xml.find_or_create_element('/root/Invoice/Line')
    assert xml.tostring() == '<root><Invoice><Line/></Invoice></root>'

    xml.find_or_create_element('/root/Invoice/Line')
    assert xml.tostring() == '<root><Invoice><Line/></Invoice></root>'

def test_facho_xml_aliases():
    xml = facho.FachoXML('root')
    xml.register_alias_xpath('Invoice', '/root/Invoice')
    invoice = xml.find_or_create_element('Invoice')
    assert xml.tostring() == '<root><Invoice/></root>'
    invoice.text = 'Test'
    assert xml.tostring() == '<root><Invoice>Test</Invoice></root>'

def test_facho_xmlns():
    xml = facho.FachoXML('root', nsmap={
        'ext': 'https://ext',
        'sts': 'https://sts',
    })

    invoiceAuthorization = xml.find_or_create_element('/root/ext:UBLExtensions/ext:UBLExtension/'
                                         'ext:ExtensionContent/sts:DianExtensions/'
                                         'sts:InvoiceControl/sts:InvoiceAuthorization')
    assert xml.tostring().strip() == '<root xmlns:ext="https://ext" xmlns:sts="https://sts"><ext:UBLExtensions>'\
        '<ext:UBLExtension>'\
        '<ext:ExtensionContent>'\
        '<sts:DianExtensions>'\
        '<sts:InvoiceControl>'\
        '<sts:InvoiceAuthorization/>'\
        '</sts:InvoiceControl></sts:DianExtensions></ext:ExtensionContent></ext:UBLExtension></ext:UBLExtensions></root>'

    invoiceAuthorization.text = '123456789'
    assert xml.tostring().strip() == '<root xmlns:ext="https://ext" xmlns:sts="https://sts"><ext:UBLExtensions>'\
        '<ext:UBLExtension>'\
        '<ext:ExtensionContent>'\
        '<sts:DianExtensions>'\
        '<sts:InvoiceControl>'\
        '<sts:InvoiceAuthorization>123456789</sts:InvoiceAuthorization>'\
        '</sts:InvoiceControl></sts:DianExtensions></ext:ExtensionContent></ext:UBLExtension></ext:UBLExtensions></root>'

def test_facho_xmlns_idempotent():
    xml = facho.FachoXML('root', nsmap={
        'ext': 'https://ext',
        'sts': 'https://sts',
    })

    xml.find_or_create_element('/root/ext:Extension/sts:Sotoros')
    assert xml.tostring() == '<root xmlns:ext="https://ext" xmlns:sts="https://sts"><ext:Extension><sts:Sotoros/></ext:Extension></root>'

    xml.find_or_create_element('/root/ext:Extension/sts:Sotoros')
    assert xml.tostring() == '<root xmlns:ext="https://ext" xmlns:sts="https://sts"><ext:Extension><sts:Sotoros/></ext:Extension></root>'

def test_facho_xml_set_element_with_format():
    xml = facho.FachoXML('root')
    invoice = xml.set_element('/root/Invoice', 1, format_='%02d')
    assert xml.tostring() == '<root><Invoice>01</Invoice></root>'

def test_facho_xml_fragment():
    xml = facho.FachoXML('root')
    invoice = xml.fragment('/root/Invoice')
    invoice.set_element('/Invoice/Id', 1)
    assert xml.tostring() == '<root><Invoice><Id>1</Id></Invoice></root>'

def test_facho_xml_fragments():
    xml = facho.FachoXML('Invoice')

    line = xml.fragment('/Invoice/Line')
    line.set_element('/Line/Id', 1)

    line = xml.fragment('/Invoice/Line', append=True)
    line.set_element('/Line/Id', 2)

    line = xml.fragment('/Invoice/Line', append=True)
    line.set_element('/Line/Id', 3)

    assert xml.tostring() == '<Invoice><Line><Id>1</Id></Line><Line><Id>2</Id></Line><Line><Id>3</Id></Line></Invoice>'

def test_facho_xml_nested_fragments():
    xml = facho.FachoXML('Invoice')
    party = xml.fragment('/Invoice/Party')
    party.set_element('/Party/Name', 'test')

    address = party.fragment('/Party/Address')
    address.set_element('/Address/Line', 'line 1')

    party.set_element('/Party/LastName', 'test')

    assert xml.tostring() == '<Invoice><Party><Name>test</Name><Address><Line>line 1</Line></Address><LastName>test</LastName></Party></Invoice>'

def test_facho_xml_get_element_text():
    xml = facho.FachoXML('Invoice')
    xml.set_element('/Invoice/ID', 'ABC123')

    assert xml.get_element_text('/Invoice/ID') == 'ABC123'

    line = xml.fragment('/Invoice/Line')
    line.set_element('/Line/Quantity', 5)
    assert line.get_element_text('/Line/Quantity', format_=int) == 5

def test_facho_xml_get_element_text_next_child():
    xml = facho.FachoXML('Invoice')
    xml.set_element('/Invoice/ID', 'ABC123')

    assert xml.get_element_text('/Invoice/ID') == 'ABC123'

    line = xml.fragment('/Invoice/Line')
    line.set_element('/Line/Quantity', 5)
    line = xml.fragment('/Invoice/Line', append=True)
    line.set_element('/Line/Quantity', 6)
    assert line.get_element_text('/Line[2]/Quantity', format_=int) == 6


def test_facho_xml_set_element_relative():
    xml = facho.FachoXML('Invoice')
    xml.set_element('./ID', 'ABC123')

    assert xml.get_element_text('/Invoice/ID') == 'ABC123'

def test_facho_xml_set_element_relative_with_namespace():
    xml = facho.FachoXML('{%s}Invoice' % ('http://www.dian.gov.co/contratos/facturaelectronica/v1'),
                         nsmap={'fe': 'http://www.dian.gov.co/contratos/facturaelectronica/v1'})
    xml.set_element('./ID', 'ABC123')

    assert xml.get_element_text('/fe:Invoice/ID') == 'ABC123'

def test_facho_xml_fragment_relative():
    xml = facho.FachoXML('root')
    invoice = xml.fragment('./Invoice')
    invoice.set_element('./Id', 1)
    assert xml.tostring() == '<root><Invoice><Id>1</Id></Invoice></root>'


def test_facho_xml_replacement_for():
    xml = facho.FachoXML('root')
    xml.placeholder_for('./child/type')
    xml.replacement_for('./child/type',
                        './child/code', 'test')
    assert xml.tostring() == '<root><child><code>test</code></child></root>'
