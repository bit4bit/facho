#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import datetime

import pytest
from facho.fe import form_xml

import helpers

def test_xml_with_required_elements():
    doc = form_xml.AttachedDocument(id='123')

    xml = doc.toFachoXML()
    assert xml.get_element_text('/atd:AttachedDocument/cbc:ID') == '123'
    
