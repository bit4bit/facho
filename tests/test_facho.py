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

def test_facho_xml_get_element_text_of_fragment():
    xml = facho.FachoXML('root')
    invoice = xml.fragment('/root/Invoice')
    invoice.set_element('/Invoice/Id', 1)
    
    assert invoice.get_element_text('/Invoice/Id') == '1'

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

def test_facho_xml_get_element_fragment_relative():
    xml = facho.FachoXML('root')
    invoice = xml.fragment('./Invoice')
    invoice.set_element('./Id', 1)
    assert invoice.get_element_text('./Id') == '1'

def test_facho_xml_replacement_for():
    xml = facho.FachoXML('root')
    xml.placeholder_for('./child/type')
    xml.replacement_for('./child/type',
                        './child/code', 'test')
    assert xml.tostring() == '<root><child><code>test</code></child></root>'

def test_facho_xml_set_element_content_invalid_validation():
    xml = facho.FachoXML('root')

    with pytest.raises(facho.FachoValueInvalid) as e:
        xml.set_element_validator('./Id', lambda text, attrs: text == 'mero')
        xml.set_element('./Id', 'bad')

def test_facho_xml_set_element_content_valid_validation():
    xml = facho.FachoXML('root')

    xml.set_element_validator('./Id', lambda text, attrs: text == 'mero')
    xml.set_element('./Id', 'mero')

def test_facho_xml_set_element_attribute_invalid_validation():
    xml = facho.FachoXML('root')

    with pytest.raises(facho.FachoValueInvalid) as e:
        xml.set_element_validator('./Id', lambda text, attrs: attrs['code'] == 'ABC')
        xml.set_element('./Id', 'mero', code = 'CBA')

def test_facho_xml_set_element_attribute_valid_validation():
    xml = facho.FachoXML('root')

    xml.set_element_validator('./Id', lambda text, attrs: attrs['code'] == 'ABC')
    xml.set_element('./Id', 'mero', code = 'ABC')

def test_facho_xml_get_element_attribute():
    xml = facho.FachoXML('root')
    xml.set_element('./Id', 'mero', code = 'ABC')
    assert xml.get_element_attribute('/root/Id', 'code') == 'ABC'

def test_facho_xml_keep_orden_slibing():
    xml = facho.FachoXML('root')
    xml.find_or_create_element('./A')
    xml.find_or_create_element('./B')
    xml.find_or_create_element('./C')
    xml.find_or_create_element('./B', append=True)
    xml.find_or_create_element('./A', append=True)

    assert xml.tostring() == '<root><A/><A/><B/><B/><C/></root>'

def test_facho_xml_placeholder_optional():
    xml = facho.FachoXML('root')
    xml.placeholder_for('./A')
    xml.placeholder_for('./B', optional=True)
    xml.placeholder_for('./C')
    
    assert xml.tostring() == '<root><A/><C/></root>'

def test_facho_xml_placeholder_append_to_optional():
    xml = facho.FachoXML('root')
    xml.placeholder_for('./A')
    xml.placeholder_for('./B', optional=True)
    xml.placeholder_for('./C')

    xml.find_or_create_element('./B')
    assert xml.tostring() == '<root><A/><B/><C/></root>'

def test_facho_xml_placeholder_set_element_to_optional():
    xml = facho.FachoXML('root')
    xml.placeholder_for('./A')
    xml.placeholder_for('./B', optional=True)
    xml.placeholder_for('./C')

    xml.set_element('./B', '2')
    assert xml.tostring() == '<root><A/><B>2</B><C/></root>'

def test_facho_xml_placeholder_set_element_to_optional_with_append():
    xml = facho.FachoXML('root')
    xml.placeholder_for('./A')
    xml.placeholder_for('./B', optional=True)
    xml.placeholder_for('./C')

    xml.set_element('./B', '2')
    xml.set_element('./B', '3', append_=True)
    assert xml.tostring() == '<root><A/><B>2</B><B>3</B><C/></root>'


def test_facho_xml_set_attributes():
    xml = facho.FachoXML('root')
    xml.find_or_create_element('./A')

    xml.set_attributes('./A',
                       value1 = '1',
                       value2 = '2'
                       )
    assert xml.get_element_attribute('/root/A', 'value1') == '1'
    assert xml.get_element_attribute('/root/A', 'value2') == '2'


def test_facho_xml_set_attributes_not_set_optional():
    xml = facho.FachoXML('root')
    xml.find_or_create_element('./A')

    xml.set_attributes('./A',
                       value1 = None,
                       value2 = '2'
                       )
    with pytest.raises(KeyError):
        xml.get_element_attribute('/root/A', 'value1')
    assert xml.get_element_attribute('/root/A', 'value2') == '2'

def test_facho_xml_placeholder_with_fragment():
    xml = facho.FachoXML('root')
    xml.placeholder_for('./A')
    xml.placeholder_for('./AA')
    xml.placeholder_for('./AAA')

    AA = xml.fragment('./AA/Child')
    AA.find_or_create_element('./B')
    AA.find_or_create_element('./B', append=True)

    AA = xml.fragment('./AA/Child', append=True)
    
    assert xml.tostring() == '<root><A/><AA><Child><B/><B/></Child><Child/></AA><AAA/></root>'

def test_facho_xml_create_on_first_append():
    xml = facho.FachoXML('root')

    xml.find_or_create_element('./A', append=True)
    assert xml.tostring() == '<root><A/></root>'

def test_facho_xml_create_on_first_append_multiple_appends():
    xml = facho.FachoXML('root')

    xml.find_or_create_element('./B', append=True)
    xml.find_or_create_element('./A', append=True)
    xml.find_or_create_element('./A', append=True)
    xml.find_or_create_element('./A', append=True)
    xml.find_or_create_element('./C', append=True)
    assert xml.tostring() == '<root><B/><A/><A/><A/><C/></root>'

def test_facho_xml_fragment_create_on_first_append():
    xml = facho.FachoXML('root')

    A = xml.fragment('./A', append=True)
    A.find_or_create_element('./B')
    A = xml.fragment('./A', append=True)
    A.find_or_create_element('./C')
    assert xml.tostring() == '<root><A><B/></A><A><C/></A></root>'

def test_facho_xml_placeholder_optional_and_fragment():
    xml = facho.FachoXML('root')

    xml.placeholder_for('./A/AA')

    A = xml.fragment('./A', append_not_exists=True)
    A.find_or_create_element('./AA/B')

    A = xml.fragment('./A', append_not_exists=True)
    A.find_or_create_element('./AA/C')

    assert xml.tostring() == '<root><A><AA><B/><C/></AA></A></root>'

def test_facho_xml_placeholder_optional_and_set_attributes():
    xml = facho.FachoXML('root')
    xml.placeholder_for('./A')

    xml.set_attributes('/root/A', prueba='OK')
    assert xml.get_element_attribute('/root/A', 'prueba') == 'OK'
    assert xml.tostring() == '<root><A prueba="OK"/></root>'

def test_facho_xml_placeholder_optional_and_fragment_with_set_element():
    xml = facho.FachoXML('root')

    xml.placeholder_for('./A/AA')

    A = xml.fragment('./A', append_not_exists=True)
    A.set_element('./AA', None, append_=True, prueba='OK')

    assert xml.tostring() == '<root><A><AA prueba="OK"/></A></root>'
    assert xml.get_element_attribute('/root/A/AA', 'prueba') == 'OK'

def test_facho_xml_exist_element():
    xml = facho.FachoXML('root')

    xml.placeholder_for('./A')
    assert xml.exist_element('/root/A') == False
    assert xml.tostring() == '<root><A/></root>'
    
    xml.find_or_create_element('./A')
    assert xml.exist_element('/root/A') == True
    assert xml.tostring() == '<root><A/></root>'

def test_facho_xml_query_element_text_or_attribute():
    xml = facho.FachoXML('root')

    xml.set_element('./A', 'contenido', clave='valor')

    assert xml.get_element_text_or_attribute('/root/A') == 'contenido'
    assert xml.get_element_text_or_attribute('/root/A/@clave') == 'valor'

def test_facho_xml_query_element_text_or_attribute_from_fragment():
    xml = facho.FachoXML('root')

    invoice = xml.fragment('/root/Invoice')
    invoice.set_element('./A', 'contenido')

    assert invoice.get_element_text_or_attribute('/Invoice/A') == 'contenido'

def test_facho_xml_build_xml_absolute():
    xml = facho.FachoXML('root')

    xpath = xml.xpath_from_root('/A')
    assert xpath == '/root/A'


def test_facho_xml_build_xml_absolute_namespace():
    xml = facho.FachoXML('{%s}root' % ('http://www.dian.gov.co/contratos/facturaelectronica/v1'),
                         nsmap={'fe': 'http://www.dian.gov.co/contratos/facturaelectronica/v1'})

    xpath = xml.xpath_from_root('/A')
    assert xpath == '/fe:root/A'


def test_facho_xml_build_xml_absolute_namespace_from_fragment():
    xml = facho.FachoXML('{%s}root' % ('http://www.dian.gov.co/contratos/facturaelectronica/v1'),
                         nsmap={'fe': 'http://www.dian.gov.co/contratos/facturaelectronica/v1'})
    invoice = xml.fragment('/root/Invoice')
    
    xpath = invoice.xpath_from_root('/A')
    assert xpath == '/fe:root/Invoice/A'

