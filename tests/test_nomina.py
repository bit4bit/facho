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
    assert xml.get_element_attribute('/fe:NominaIndividual/Devengados/Basico', 'SueldoTrabajado') == '1000000.00'

def test_adicionar_devengado_transporte():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoTransporte(
        auxilio_transporte = fe.nomina.Amount(2_000_000)
    ))

    xml = nomina.toFachoXML()

    assert xml.get_element_attribute('/fe:NominaIndividual/Devengados/Transporte', 'AuxilioTransporte') == '2000000.0'

def test_adicionar_devengado_comprobante_total():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 60,
        sueldo_trabajado = fe.nomina.Amount(2_000_000)
    ))

    nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
        porcentaje = fe.nomina.Amount(19),
        deduccion = fe.nomina.Amount(1_000_000)
    ))


    xml = nomina.toFachoXML()

    assert xml.get_element_text('/fe:NominaIndividual/ComprobanteTotal') == '1000000.00'

def test_adicionar_devengado_comprobante_total_cero():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 60,
        sueldo_trabajado = fe.nomina.Amount(1_000_000)
    ))

    nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
        porcentaje = fe.nomina.Amount(19),
        deduccion = fe.nomina.Amount(1_000_000)
    ))

    xml = nomina.toFachoXML()

    assert xml.get_element_text('/fe:NominaIndividual/ComprobanteTotal') == '0.00'

def test_adicionar_devengado_transporte_muchos():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoTransporte(
        auxilio_transporte = fe.nomina.Amount(2_000_000)
    ))

    nomina.adicionar_devengado(fe.nomina.DevengadoTransporte(
        auxilio_transporte = fe.nomina.Amount(3_000_000)
    ))

    xml = nomina.toFachoXML()
    print(xml)
    assert xml.get_element_text('/fe:NominaIndividual/DevengadosTotal') == '5000000.00'

def test_adicionar_deduccion_salud():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 60,
        sueldo_trabajado = fe.nomina.Amount(1000)
    ))

    nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
        porcentaje = fe.nomina.Amount(19),
        deduccion = fe.nomina.Amount(1000)
    ))

    xml = nomina.toFachoXML()
    print(xml)
    assert xml.get_element_text('/fe:NominaIndividual/DeduccionesTotal') == '1000.00'

def test_nomina_obligatorios_segun_anexo_tecnico():
    nomina = fe.nomina.DIANNominaIndividual()

    errors = nomina.validate()

    assert_error(errors, 'se requiere Periodo')
    assert_error(errors, 'se requiere DevengadoBasico')
    assert_error(errors, 'se requiere DeduccionSalud')
    assert_error(errors, 'se requiere DeduccionFondoPension')

def test_nomina_cune():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.asignar_numero_secuencia(fe.nomina.NumeroSecuencia(
        numero = 'N00001'
        ))

    nomina.asignar_informacion_general(fe.nomina.InformacionGeneral(
        fecha_generacion = '2020-01-16',
        hora_generacion = '1053:10-05:00',
        tipo_ambiente = fe.nomina.InformacionGeneral.AMBIENTE_PRODUCCION,
        software_pin = '693'
    ))

    nomina.asignar_empleador(fe.nomina.Empleador(
        nit = '700085371',
    ))

    nomina.asignar_trabajador(fe.nomina.Trabajador(
        numero_documento = '800199436'
    ))

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 60,
        sueldo_trabajado = fe.nomina.Amount(3_500_000)
    ))

    nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
        porcentaje = fe.nomina.Amount(19),
        deduccion = fe.nomina.Amount(1_000_000)
    ))

    xml = nomina.toFachoXML()
    # TODO(bit4bit) no logro generar cune igual al del anexo tecnico
    #assert xml.get_element_attribute('/fe:NominaIndividual/InformacionGeneral', 'CUNE') == '16560dc8956122e84ffb743c817fe7d494e058a44d9ca3fa4c234c268b4f766003253fbee7ea4af9682dd57210f3bac2'
    assert xml.get_element_attribute('/fe:NominaIndividual/InformacionGeneral', 'CUNE') == 'b8f9b6c24de07ffd92ea5467433a3b69357cfaffa7c19722db94b2e0eca41d057085a54f484b5da15ff585e773b0b0ab'

def assert_error(errors, msg):
    for error in errors:
        if str(error) == msg:
            return True

    raise "wants error: %s" % (msg)

