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
    inv = form.Invoice()
    inv.add_invoice_line(form.InvoiceLine(
        quantity = 1,
        description = 'producto facho',
        item = form.StandardItem('test', 9999),
        price = form.Price(
            amount = 100.0,
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
    assert inv.invoice_legal_monetary_total.line_extension_amount == 100.0
    assert inv.invoice_legal_monetary_total.tax_exclusive_amount == 100.0
    assert inv.invoice_legal_monetary_total.tax_inclusive_amount == 119.0
    assert inv.invoice_legal_monetary_total.charge_total_amount == 0.0


def test_FAU10():
    inv = form.Invoice()
    inv.add_invoice_line(form.InvoiceLine(
        quantity = 1,
        description = 'producto facho',
        item = form.StandardItem('test', 9999),
        price = form.Price(
            amount = 100.0,
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
    inv.add_allownace_charge(form.AllowanceCharge(amount=19.0))

    inv.calculate()
    assert inv.invoice_legal_monetary_total.line_extension_amount == 100.0
    assert inv.invoice_legal_monetary_total.tax_exclusive_amount == 100.0
    assert inv.invoice_legal_monetary_total.tax_inclusive_amount == 119.0
    assert inv.invoice_legal_monetary_total.charge_total_amount == 19.0
