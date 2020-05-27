#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest
from datetime import datetime
import io
import zipfile

import facho.fe.form as form
from facho import fe



@pytest.fixture
def simple_invoice():
    inv = form.Invoice()
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('ABC123')
    inv.set_supplier(form.Party(
        name = 'facho-supplier',
        ident = 123,
        responsability_code = 'No aplica',
        organization_code = 'Persona Natural'
    ))
    inv.set_customer(form.Party(
        name = 'facho-customer',
        ident = 321,
        responsability_code = 'No aplica',
        organization_code = 'Persona Natural'
    ))
    inv.add_invoice_line(form.InvoiceLine(
        quantity = 1,
        description = 'producto facho',
        item_ident = 9999,
        price_amount = 100.0,
        tax = form.TaxTotal(
            tax_amount = 0.0,
            taxable_amount = 0.0,
            subtotals = [
                form.TaxSubTotal(
                    percent = 19.0,
                )
            ]
        )
    ))
    return inv


def test_invoicesimple_build(simple_invoice):
    invoice_validator = form.DianResolucion0001Validator()
    simple_invoice.validate(invoice_validator)
    assert invoice_validator.valid() == True
    xml = form.DIANInvoiceXML(simple_invoice)

    supplier_name = xml.get_element_text('/fe:Invoice/fe:AccountingSupplierParty/fe:Party/cac:PartyName/cbc:Name')
    assert supplier_name == simple_invoice.invoice_supplier.name

    supplier_identification_number = xml.get_element_text('/fe:Invoice/fe:AccountingSupplierParty/fe:Party/cac:PartyIdentification/cbc:ID')
    assert int(supplier_identification_number) == simple_invoice.invoice_supplier.ident

    customer_name = xml.get_element_text('/fe:Invoice/fe:AccountingCustomerParty/fe:Party/cac:PartyName/cbc:Name')
    assert customer_name == simple_invoice.invoice_customer.name

    customer_identification_number = xml.get_element_text('/fe:Invoice/fe:AccountingCustomerParty/fe:Party/cac:PartyIdentification/cbc:ID')
    assert int(customer_identification_number) == simple_invoice.invoice_customer.ident


def test_invoicesimple_build_with_cufe(simple_invoice):
    invoice_validator = form.DianResolucion0001Validator()
    simple_invoice.validate(invoice_validator)
    assert invoice_validator.valid() == True
    xml = form.DIANInvoiceXML(simple_invoice)
    cufe = xml.get_element_text('/fe:Invoice/cbc:UUID')
    assert cufe != ''


def test_invoicesimple_xml_signed(monkeypatch, simple_invoice):
    invoice_validator = form.DianResolucion0001Validator()
    simple_invoice.validate(invoice_validator)
    assert invoice_validator.valid() == True
    xml = form.DIANInvoiceXML(simple_invoice)

    signer = fe.DianXMLExtensionSigner('./tests/example.p12')
    xml.add_extension(signer)

    with monkeypatch.context() as m:
        import helpers
        helpers.mock_urlopen(m)
        xml.attach_extensions()

    elem = xml.find_or_create_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature')
    assert elem.text is not None

def test_invoicesimple_zip(simple_invoice):
    xml_invoice = form.DIANInvoiceXML(simple_invoice)
    
    zipdata = io.BytesIO()
    with fe.DianZIP(zipdata) as dianzip:
        name_invoice = dianzip.add_invoice_xml(simple_invoice.invoice_ident, str(xml_invoice))

    with zipfile.ZipFile(zipdata) as dianzip:
        xml_data = dianzip.open(name_invoice).read().decode('utf-8')
        assert xml_data == str(xml_invoice)


def test_bug_cbcid_empty_on_invoice_line(simple_invoice):
    xml_invoice = form.DIANInvoiceXML(simple_invoice)
    print(str(xml_invoice))

    cbc_id = xml_invoice.get_element_text('/fe:Invoice/fe:InvoiceLine[1]/cbc:ID', format_=int)
    assert cbc_id == 1
