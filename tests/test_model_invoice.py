#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Nuevo esquema para modelar segun decreto"""

from datetime import datetime

import pytest

import facho.fe.model as model
import facho.fe.form as form

def test_simple_invoice():
    invoice = model.Invoice()
    invoice.id = '323200000129'
    invoice.issue = datetime.strptime('2019-01-16 10:53:10-05:00', '%Y-%m-%d %H:%M:%S%z')
    invoice.supplier.party.id = '700085371'
    invoice.customer.party.id = '800199436'

    line = invoice.lines.create()
    line.quantity = form.Quantity(1, '94')
    line.price = form.Amount(5_000)
    subtotal = line.taxtotal.subtotals.create()
    subtotal.percent = 19.0

    assert '<Invoice><ID>323200000129</ID><IssueDate>2019-01-16T10:53:10-05:00</IssueDate><IssueTime>10:5310-05:00</IssueTime><AccountingSupplierParty><Party><ID>700085371</ID></Party></AccountingSupplierParty><AccountingCustomerParty><Party><ID>800199436</ID></Party></AccountingCustomerParty><InvoiceLine><InvoiceQuantity unitCode="NAR">1.0</InvoiceQuantity><TaxTotal><TaxSubTotal><TaxCategory><Percent>19.0</Percent><TaxScheme><ID>01</ID><Name>IVA</Name></TaxScheme></TaxCategory></TaxSubTotal></TaxTotal><Price><PriceAmount currencyID="COP">5000.0</PriceAmount></Price></InvoiceLine></Invoice>' == invoice.to_xml()
