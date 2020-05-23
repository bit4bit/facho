#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest
import facho.fe.data.dian as dian

def test_dian():
    assert dian.TipoResponsabilidad.short_name == 'TipoResponsabilidad'
    assert dian.TipoResponsabilidad['Autorretenedor']['name'] == 'Autorretenedor'

    assert dian.TipoOrganizacion.short_name == 'TipoOrganizacion'
    assert dian.TipoOrganizacion['Persona Natural']['name'] == 'Persona Natural'
