#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import pytest

import facho.fe.form as form
from facho import fe
from facho.fe.form_xml import DIANInvoiceXML, DIANCreditNoteXML, DIANDebitNoteXML

from fixtures import *

from facho.fe.form import query

def test_query_billing_reference(simple_invoice):
    xml = DIANInvoiceXML(simple_invoice)
    cufe_extension = fe.DianXMLExtensionCUFE(simple_invoice)
    xml.add_extension(cufe_extension)
    out = xml.tostring()
    
    reference = query.billing_reference(out, form.BillingReference)
    assert isinstance(reference, form.BillingReference)
    assert reference.ident != ''
    assert reference.uuid != ''
    assert reference.date != ''
