#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest
from datetime import datetime
import copy

from facho.fe import form
from facho.fe import form_xml

from fixtures import *

def test_import_DIANInvoiceXML():
    try:
        form_xml.DIANInvoiceXML
    except AttributeError:
        pytest.fail("unexpected not found")


def test_import_DIANDebitNoteXML():
    try:
        form_xml.DIANDebitNoteXML
    except AttributeError:
        pytest.fail("unexpected not found")

def test_import_DIANCreditNoteXML():
    try:
        form_xml.DIANCreditNoteXML
    except AttributeError:
        pytest.fail("unexpected not found")

def test_allowance_charge_in_invoice(simple_invoice_without_lines):
    inv = copy.copy(simple_invoice_without_lines)
    inv.add_invoice_line(form.InvoiceLine(
        quantity = form.Quantity(1, '94'),
        description = 'producto facho',
        item = form.StandardItem(9999),
        price = form.Price(
            amount = form.Amount(100.0),
            type_code = '01',
            type = 'x'
        ),
        tax = form.TaxTotal(
            subtotals = [
                form.TaxSubTotal(
                    percent = 19.0,
                )
            ]
        )
    ))
    inv.add_allowance_charge(form.AllowanceCharge(amount=form.Amount(19.0)))
    inv.calculate()
    
    xml = form_xml.DIANInvoiceXML(inv)
    assert xml.get_element_text('./cac:AllowanceCharge/cbc:ID') == '1'
    assert xml.get_element_text('./cac:AllowanceCharge/cbc:ChargeIndicator') == 'true'
    assert xml.get_element_text('./cac:AllowanceCharge/cbc:Amount') == '19.0'
    assert xml.get_element_text('./cac:AllowanceCharge/cbc:BaseAmount') == '100.0'

def test_allowance_charge_in_invoice_line(simple_invoice_without_lines):
    inv = copy.copy(simple_invoice_without_lines)
    inv.add_invoice_line(form.InvoiceLine(
        quantity = form.Quantity(1, '94'),
        description = 'producto facho',
        item = form.StandardItem(9999),
        price = form.Price(
            amount = form.Amount(100.0),
            type_code = '01',
            type = 'x'
        ),
        tax = form.TaxTotal(
            subtotals = [
                form.TaxSubTotal(
                    percent = 19.0,
                )
            ]
        ),
        allowance_charge = [
            form.AllowanceChargeAsDiscount(amount=form.Amount(10.0))
        ]
    ))
    inv.calculate()

    # se aplico descuento
    assert inv.invoice_legal_monetary_total.line_extension_amount == form.Amount(90.0)
    
    xml = form_xml.DIANInvoiceXML(inv)

    with pytest.raises(AttributeError):
        assert xml.get_element_text('/fe:Invoice/cac:AllowanceCharge/cbc:ID') == '1'
    xml.get_element_text('/fe:Invoice/cac:InvoiceLine/cac:AllowanceCharge/cbc:ID') == '1'
    xml.get_element_text('/fe:Invoice/cac:InvoiceLine/cac:AllowanceCharge/cbc:BaseAmount') == '100.0'
