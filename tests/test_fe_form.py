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
def simple_invoice_without_lines():
    inv = form.Invoice()
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('ABC123')
    inv.set_payment_mean_debit('1234', '41', datetime.now())
    inv.set_supplier(form.Party(
        name = 'facho-supplier',
        ident = 123,
        responsability_code = 'ZZ',
        organization_code = '1',
        address = form.Address(name='Test Building')
    ))
    inv.set_customer(form.Party(
        name = 'facho-customer',
        ident = 321,
        responsability_code = 'ZZ',
        organization_code = '1',
        address = form.Address(name='Test Building')
    ))
    return inv

@pytest.fixture
def simple_invoice():
    inv = form.Invoice()
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('ABC123')
    inv.set_payment_mean_debit('1234', '41', datetime.now())
    inv.set_supplier(form.Party(
        name = 'facho-supplier',
        ident = 123,
        responsability_code = 'ZZ',
        organization_code = '1'
    ))
    inv.set_customer(form.Party(
        name = 'facho-customer',
        ident = 321,
        responsability_code = 'ZZ',
        organization_code = '1'
    ))
    inv.add_invoice_line(form.InvoiceLine(
        quantity = 1,
        description = 'producto facho',
        item = form.StandardItem('test', 9999),
        price = form.Price(100.0, '01', ''),
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
    assert invoice_validator.validate(simple_invoice) == True
    xml = form.DIANInvoiceXML(simple_invoice)

    supplier_name = xml.get_element_text('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name')
    assert supplier_name == simple_invoice.invoice_supplier.name

    customer_name = xml.get_element_text('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name')
    assert customer_name == simple_invoice.invoice_customer.name


def test_invoicesimple_build_with_cufe(simple_invoice):
    invoice_validator = form.DianResolucion0001Validator()
    assert invoice_validator.validate(simple_invoice) == True
    xml = form.DIANInvoiceXML(simple_invoice)
    cufe_extension = fe.DianXMLExtensionCUFE(simple_invoice)
    xml.add_extension(cufe_extension)
    cufe = xml.get_element_text('/fe:Invoice/cbc:UUID')
    assert cufe != ''


def test_invoicesimple_xml_signed(monkeypatch, simple_invoice):
    invoice_validator = form.DianResolucion0001Validator()
    assert invoice_validator.validate(simple_invoice) == True
    xml = form.DIANInvoiceXML(simple_invoice)

    signer = fe.DianXMLExtensionSigner('./tests/example.p12')


    with monkeypatch.context() as m:
        import helpers
        helpers.mock_urlopen(m)
        xml.add_extension(signer)
        
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
    cbc_id = xml_invoice.get_element_text('/fe:Invoice/cac:InvoiceLine[1]/cbc:ID', format_=int)
    assert cbc_id == 1

def test_invoice_line_count_numeric(simple_invoice):
    xml_invoice = form.DIANInvoiceXML(simple_invoice)
    count = xml_invoice.get_element_text('/fe:Invoice/cbc:LineCountNumeric', format_=int)
    assert count == len(simple_invoice.invoice_lines)
    
def test_invoice_profileexecutionid(simple_invoice):
    xml_invoice = form.DIANInvoiceXML(simple_invoice)
    cufe_extension = fe.DianXMLExtensionCUFE(simple_invoice)
    xml_invoice.add_extension(cufe_extension)
    id_ = xml_invoice.get_element_text('/fe:Invoice/cbc:ProfileExecutionID', format_=int)
    assert id_ == 2

def test_invoice_invoice_type_code(simple_invoice):
    xml_invoice = form.DIANInvoiceXML(simple_invoice)
    id_ = xml_invoice.get_element_text('/fe:Invoice/cbc:InvoiceTypeCode', format_=int)
    assert id_ == 1

def test_invoice_totals(simple_invoice_without_lines):
    simple_invoice = simple_invoice_without_lines
    simple_invoice.invoice_ident = '323200000129'
    simple_invoice.invoice_issue = datetime.strptime('2019-01-16 10:53:10-05:00', '%Y-%m-%d %H:%M:%S%z')
    simple_invoice.invoice_supplier.ident = '700085371'
    simple_invoice.invoice_customer.ident = '800199436'
    simple_invoice.add_invoice_line(form.InvoiceLine(
        quantity = 1,
        description = 'producto',
        item = form.StandardItem('test', 9999),
        price = form.Price(1_500_000, '', ''),
        tax = form.TaxTotal(
            subtotals = [
                form.TaxSubTotal(
                    tax_scheme_ident = '01',
                    percent = 19.0
                )])
    ))
    simple_invoice.calculate()
    assert 1 == len(simple_invoice.invoice_lines)
    assert 1_500_000 == simple_invoice.invoice_legal_monetary_total.line_extension_amount
    assert 1_785_000 == simple_invoice.invoice_legal_monetary_total.payable_amount

def test_invoice_cufe(simple_invoice_without_lines):
    simple_invoice = simple_invoice_without_lines
    simple_invoice.invoice_ident = '323200000129'
    simple_invoice.invoice_issue = datetime.strptime('2019-01-16 10:53:10-05:00', '%Y-%m-%d %H:%M:%S%z')
    simple_invoice.invoice_supplier.ident = '700085371'
    simple_invoice.invoice_customer.ident = '800199436'
    simple_invoice.add_invoice_line(form.InvoiceLine(
        quantity = 1,
        description = 'producto',
        item = form.StandardItem('test', 111),
        price = form.Price(1_500_000, '', ''),
        tax = form.TaxTotal(
            subtotals = [
                form.TaxSubTotal(
                    tax_scheme_ident = '01',
                    percent = 19.0
                )])
    ))
            
    class FakeDianXMLExtensionCUFE(fe.DianXMLExtensionCUFE):
        def issue_time(self, datetime_):
            return '10:53:10-05:00'
        def issue_date(self, datetime_):
            return '2019-01-16'

    xml_invoice = form.DIANInvoiceXML(simple_invoice)
                                     
    cufe_extension = FakeDianXMLExtensionCUFE(
        simple_invoice,
        tipo_ambiente = fe.DianXMLExtensionCUFE.AMBIENTE_PRODUCCION,
        clave_tecnica = '693ff6f2a553c3646a063436fd4dd9ded0311471'
    )
    xml_invoice.add_extension(cufe_extension)
    cufe = xml_invoice.get_element_text('/fe:Invoice/cbc:UUID')
    # RESOLUCION 004: pagina 689
    assert cufe == '8bb918b19ba22a694f1da11c643b5e9de39adf60311cf179179e9b33381030bcd4c3c3f156c506ed5908f9276f5bd9b4'



def test_invoice_payment_mean(monkeypatch, simple_invoice):
    invoice_validator = form.DianResolucion0001Validator()
    assert invoice_validator.validate(simple_invoice) == True
