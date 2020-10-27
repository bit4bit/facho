#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest

from facho.fe import form_xml

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
