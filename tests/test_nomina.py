#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest

from facho import fe

def test_adicionar_devengado_Basico():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 30,
        sueldo_trabajado = fe.nomina.Amount(1_000_000)
    ))

    xml = nomina.toFachoXML()
    assert xml.get_element_attribute('/fe:NominaIndividual/Devengados/Basico', 'DiasTrabajados') == '30'
    assert xml.get_element_attribute('/fe:NominaIndividual/Devengados/Basico', 'SueldoTrabajado') == '1000000.0'
