#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""
import re

import pytest

from facho import fe

import helpers

def atest_nomina_ajuste_reemplazar():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    xml = nomina.toFachoXML()
    print(xml)
    assert False

def test_nomina_ajuste_reemplazar_asignacion_tipo_xml():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()
    nomina.asignar_metadata(fe.nomina.Metadata(
        novedad=fe.nomina.Novedad(
            activa = True,
            cune = "N0111"
        ),
        secuencia=fe.nomina.NumeroSecuencia(
            prefijo = 'N',
            consecutivo='00001'
        ),
        lugar_generacion=fe.nomina.Lugar(
            pais = fe.nomina.Pais(
                code = 'CO'
            ),
            departamento = fe.nomina.Departamento(
                code = '05'
            ),
            municipio = fe.nomina.Municipio(
                code = '05001'
            ),
        ),
        proveedor=fe.nomina.Proveedor(
            nit='999999',
            dv=2,
            software_id='xx',
            software_pin='12',
            razon_social='facho'
        )
    ))
    nomina.asignar_empleador(fe.nomina.Empleador(
        razon_social='facho',
        nit = '700085371',
        dv = '1',
        pais = fe.nomina.Pais(
            code = 'CO'
        ),
        departamento = fe.nomina.Departamento(
            code = '05'
        ),
        municipio = fe.nomina.Municipio(
            code = '05001'
        ),
        direccion = 'calle etrivial'
    ))

    nomina.asignar_trabajador(fe.nomina.Trabajador(
        tipo_contrato = fe.nomina.TipoContrato(
            code = '1'
        ),
        alto_riesgo = False,
        tipo_documento = fe.nomina.TipoDocumento(
            code = '11'
        ),
        primer_apellido = 'gnu',
        segundo_apellido = 'emacs',
        primer_nombre = 'facho',
        lugar_trabajo = fe.nomina.LugarTrabajo(
            pais = fe.nomina.Pais(code='CO'),
            departamento = fe.nomina.Departamento(code='05'),
            municipio = fe.nomina.Municipio(code='05001'),
            direccion = 'calle facho'
        ),
        numero_documento = '800199436',
        tipo = fe.nomina.TipoTrabajador(
            code = '01'
        ),
        salario_integral = True,
        sueldo = fe.nomina.Amount(1_500_000)
    ))
    nomina.asignar_informacion_general(fe.nomina.InformacionGeneral(
        fecha_generacion = '2020-01-16',
        hora_generacion = '1053:10-05:00',
        tipo_ambiente = fe.nomina.InformacionGeneral.AMBIENTE_PRODUCCION,
        software_pin = '693',
        tipo_xml = fe.nomina.InformacionGeneral.TIPO_XML_AJUSTES,
        periodo_nomina = fe.nomina.PeriodoNomina(code='1'),
        tipo_moneda = fe.nomina.TipoMoneda(code='COP')
    ))

    xml = nomina.toFachoXML()

    assert xml.get_element_attribute('/nominaajuste:NominaIndividualDeAjuste/Reemplazar/InformacionGeneral', 'TipoXML') == '103'


def test_adicionar_reemplazar_devengado_comprobante_total():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 60,
        sueldo_trabajado = fe.nomina.Amount(2_000_000)
    ))

    nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
        porcentaje = fe.nomina.Amount(19),
        deduccion = fe.nomina.Amount(1_000_000)
    ))

    xml = nomina.toFachoXML()

    assert xml.get_element_text('/nominaajuste:NominaIndividualDeAjuste/Reemplazar/ComprobanteTotal') == '1000000.00'


def test_adicionar_reemplazar_asignar_predecesor():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element_text_or_attribute('/nominaajuste:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@NumeroPred') == '123456'
    assert xml.get_element_text_or_attribute('/nominaajuste:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@CUNEPred') == 'ABC123456'
    assert xml.get_element_text_or_attribute('/nominaajuste:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@FechaGenPred') == '2021-11-16'


def test_adicionar_reemplazar_eliminar_predecesor_opcional():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())

    assert xml.get_element('/nominaajuste:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor') is not None
    assert xml.get_element('/nominaajuste:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor') is None

def test_adicionar_eliminar_reemplazar_predecesor_opcional():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Eliminar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Eliminar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element('/nominaajuste:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor') is not None
    assert xml.get_element('/nominaajuste:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor') is None

def test_adicionar_eliminar_devengado_comprobante_total():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Eliminar()

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 60,
        sueldo_trabajado = fe.nomina.Amount(2_000_000)
    ))

    nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
        porcentaje = fe.nomina.Amount(19),
        deduccion = fe.nomina.Amount(1_000_000)
    ))

    xml = nomina.toFachoXML()

    assert xml.get_element_text('/nominaajuste:NominaIndividualDeAjuste/Eliminar/ComprobanteTotal') == '1000000.00'

def test_adicionar_eliminar_asignar_predecesor():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Eliminar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Eliminar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element_text_or_attribute('/nominaajuste:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@NumeroPred') == '123456'
    assert xml.get_element_text_or_attribute('/nominaajuste:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@CUNEPred') == 'ABC123456'
    assert xml.get_element_text_or_attribute('/nominaajuste:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@FechaGenPred') == '2021-11-16'

def test_nomina_devengado_horas_extras_diarias():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoHorasExtrasDiarias(
        horas_extras=[
            fe.nomina.DevengadoHoraExtra(
                hora_inicio='2021-11-30T19:09:55',
                hora_fin='2021-11-30T20:09:55',
                cantidad=1,
                porcentaje=fe.nomina.Amount(1),
                pago=fe.nomina.Amount(100)
            ),
            fe.nomina.DevengadoHoraExtra(
                hora_inicio='2021-11-30T18:09:55',
                hora_fin='2021-11-30T19:09:55',
                cantidad=2,
                porcentaje=fe.nomina.Amount(2),
                pago=fe.nomina.Amount(200)
            )
        ]
    ))

    xml = nomina.toFachoXML()
    extras = xml.get_element('/nomina:NominaIndividual/Devengados/HEDs/HED', multiple=True)
    assert extras[0].get('HoraInicio') == '2021-11-30T19:09:55'
    assert extras[0].get('HoraFin') == '2021-11-30T20:09:55'
    assert extras[0].get('Cantidad') == '1'
    assert extras[0].get('Porcentaje') == '1.00'
    assert extras[0].get('Pago') == '100.00'
    assert extras[1].get('HoraInicio') == '2021-11-30T18:09:55'
    assert extras[1].get('HoraFin') == '2021-11-30T19:09:55'
    assert extras[1].get('Cantidad') == '2'
    assert extras[1].get('Porcentaje') == '2.00'
    assert extras[1].get('Pago') == '200.00'
