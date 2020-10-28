#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest
from facho.fe.data.dian import codelist

def test_tiporesponsabilidad():
    assert codelist.TipoResponsabilidad.short_name == 'TipoResponsabilidad'
    assert codelist.TipoResponsabilidad.by_name('Autorretenedor')['name'] == 'Autorretenedor'

def test_tipoorganizacion():
    assert codelist.TipoOrganizacion.short_name == 'TipoOrganizacion'
    assert codelist.TipoOrganizacion.by_name('Persona Natural')['name'] == 'Persona Natural'

def test_tipodocumento():
    assert codelist.TipoDocumento.short_name == 'TipoDocumento'
    assert codelist.TipoDocumento.by_name('Factura de Venta Nacional')['code'] == '01'

def test_departamento():
    assert codelist.Departamento['05']['name'] == 'Antioquia'
