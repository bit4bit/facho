#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Nuevo esquema para modelar segun decreto"""

from datetime import datetime

import pytest

import facho.fe.model as model

def test_simple_invoice():
    invoice = model.Invoice()
    invoice.id = '323200000129'
    invoice.issue = datetime.strptime('2019-01-16 10:53:10-05:00', '%Y-%m-%d %H:%M:%S%z')
    invoice.supplier.party.id = '700085371'
    invoice.customer.party.id = '800199436'
