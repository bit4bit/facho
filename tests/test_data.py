#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest
from facho.fe.data.dian import codelist

def test_dian():
    assert codelist.TipoResponsabilidad.short_name == 'TipoResponsabilidad'
    assert codelist.TipoResponsabilidad['Autorretenedor']['name'] == 'Autorretenedor'

    assert codelist.TipoOrganizacion.short_name == 'TipoOrganizacion'
    assert codelist.TipoOrganizacion['Persona Natural']['name'] == 'Persona Natural'
