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

def test_invoice_legalmonetary():
    inv = form.NationalSalesInvoice()
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
    inv.calculate()
    assert inv.invoice_legal_monetary_total.line_extension_amount == form.Amount(100.0)
    assert inv.invoice_legal_monetary_total.tax_exclusive_amount == form.Amount(100.0)
    assert inv.invoice_legal_monetary_total.tax_inclusive_amount == form.Amount(119.0)
    assert inv.invoice_legal_monetary_total.charge_total_amount == form.Amount(0.0)

def test_allowancecharge_as_discount():
    discount = form.AllowanceChargeAsDiscount(amount=form.Amount(1000.0))
    assert discount.isDiscount() == True
    
def test_FAU10():
    inv = form.NationalSalesInvoice()
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
    assert inv.invoice_legal_monetary_total.line_extension_amount == form.Amount(100.0)
    assert inv.invoice_legal_monetary_total.tax_exclusive_amount == form.Amount(100.0)
    assert inv.invoice_legal_monetary_total.tax_inclusive_amount == form.Amount(119.0)
    assert inv.invoice_legal_monetary_total.charge_total_amount == form.Amount(19.0)


def test_FAU14():
    inv = form.NationalSalesInvoice()
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
    inv.add_prepaid_payment(form.PrePaidPayment(paid_amount = form.Amount(50.0)))
    inv.calculate()

    wants = form.Amount(119.0 + 19.0 - 50.0)

    assert inv.invoice_legal_monetary_total.payable_amount == wants, "got %s want %s" % (inv.invoice_legal_monetary_total.payable_amount, wants)


def test_invalid_tipo_operacion_nota_debito():
    reference = form.InvoiceDocumentReference(
        ident = '11111',
        uuid = '21312312',
        date = '2020-05-05'
    )
    inv = form.DebitNote(reference)
    with pytest.raises(ValueError):
        inv.set_operation_type(22)

def test_valid_tipo_operacion_nota_debito():
    reference = form.InvoiceDocumentReference(
        ident = '11111',
        uuid = '21312312',
        date = '2020-05-05'
    )
    inv = form.DebitNote(reference)
    inv.set_operation_type('30')

def test_invalid_tipo_operacion_nota_credito():
    reference = form.InvoiceDocumentReference(
        ident = '11111',
        uuid = '21312312',
        date = '2020-05-05'
    )
    inv = form.DebitNote(reference)
    with pytest.raises(ValueError):
        inv.set_operation_type('990')

def test_valid_tipo_operacion_nota_credito():
    reference = form.InvoiceDocumentReference(
        ident = '11111',
        uuid = '21312312',
        date = '2020-05-05'
    )
    inv = form.CreditNote(reference)
    inv.set_operation_type('20')


def test_quantity():
    quantity1 = form.Quantity(10, '94')
    assert quantity1 * form.Amount(3) == form.Amount(30)

def test_invoice_line_quantity_without_taxes():
    line = form.InvoiceLine(
        quantity = form.Quantity(10, '94'),
        description = '',
        item = form.StandardItem('test', 9999),
        price = form.Price(
            amount = form.Amount(30.00),
            type_code = '01',
            type = 'x'
        ),
        tax = form.TaxTotal(subtotals=[]))
    line.calculate()
    assert line.total_amount == form.Amount(300)
    assert line.tax_amount == form.Amount(0)

def test_invoice_legalmonetary_with_taxes():
    inv = form.NationalSalesInvoice()
    inv.add_invoice_line(form.InvoiceLine(
        quantity = form.Quantity(1, '94'),
        description = 'producto facho',
        item = form.StandardItem(9999),
        price = form.Price(
            amount = form.Amount(100.0),
            type_code = '01',
            type = 'x'
        ),
        tax = form.TaxTotal(subtotals=[])
    ))
    inv.calculate()

    assert inv.invoice_legal_monetary_total.line_extension_amount == form.Amount(100.0)
    assert inv.invoice_legal_monetary_total.tax_exclusive_amount == form.Amount(100.0)
    assert inv.invoice_legal_monetary_total.tax_inclusive_amount == form.Amount(100.0)
    assert inv.invoice_legal_monetary_total.charge_total_amount == form.Amount(0.0)
    assert inv.invoice_legal_monetary_total.payable_amount == form.Amount(100.0)


def test_invoice_ident_prefix_automatic_invalid():
    inv = form.NationalSalesInvoice()
    with pytest.raises(ValueError):
        inv.set_ident('SETPQJQJ1234567')

def test_invoice_ident_prefix_automatic():
    inv = form.NationalSalesInvoice()
    inv.set_ident('SETP1234567')
    assert inv.invoice_ident_prefix == 'SETP'
    inv = form.NationalSalesInvoice()
    inv.set_ident('SET1234567')
    assert inv.invoice_ident_prefix == 'SET'
    inv = form.NationalSalesInvoice()
    inv.set_ident('SE1234567')
    assert inv.invoice_ident_prefix == 'SE'
    inv = form.NationalSalesInvoice()
    inv.set_ident('S1234567')
    assert inv.invoice_ident_prefix == 'S'
    inv = form.NationalSalesInvoice()
    inv.set_ident('1234567')
    assert inv.invoice_ident_prefix == ''

def test_invoice_ident_prefix_manual():
    inv = form.NationalSalesInvoice()
    inv.set_ident('SETP1234567')
    inv.set_ident_prefix('SETA')
    assert inv.invoice_ident_prefix == 'SETA'

def test_invoice_ident_prefix_automatic_debit():
    inv = form.DebitNote(form.BillingReference('','',''))
    inv.set_ident('ABCDEF1234567')
    assert inv.invoice_ident_prefix == 'ABCDEF'
