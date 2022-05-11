#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""
import re

import pytest

from facho import fe

import helpers

def assert_error(errors, msg):
    for error in errors:
        if str(error) == msg:
            return True

    raise "wants error: %s" % (msg)

def test_adicionar_devengado_Basico():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 30,
        sueldo_trabajado = fe.nomina.Amount(1_000_000)
    ))

    xml = nomina.toFachoXML()
    assert xml.get_element_attribute('/nomina:NominaIndividual/Devengados/Basico', 'DiasTrabajados') == '30'
    assert xml.get_element_attribute('/nomina:NominaIndividual/Devengados/Basico', 'SueldoTrabajado') == '1000000.00'

def test_adicionar_devengado_transporte():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoTransporte(
        auxilio_transporte = fe.nomina.Amount(2_000_000)
    ))

    xml = nomina.toFachoXML()

    assert xml.get_element_attribute('/nomina:NominaIndividual/Devengados/Transporte', 'AuxilioTransporte') == '2000000.0'

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

    assert xml.get_element_text('/nomina:NominaIndividual/ComprobanteTotal') == '1000000.00'

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

    assert xml.get_element_text('/nomina:NominaIndividual/ComprobanteTotal') == '0.00'

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
    assert xml.get_element_text('/nomina:NominaIndividual/DevengadosTotal') == '5000000.00'

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
    assert xml.get_element_text('/nomina:NominaIndividual/DeduccionesTotal') == '1000.00'

def test_nomina_obligatorios_segun_anexo_tecnico():
    nomina = fe.nomina.DIANNominaIndividual()

    errors = nomina.validate()

    assert_error(errors, 'se requiere Periodo')
    assert_error(errors, 'se requiere DevengadoBasico')
    assert_error(errors, 'se requiere DeduccionSalud')
    assert_error(errors, 'se requiere DeduccionFondoPension')

def test_nomina_xml():
    nomina = fe.nomina.DIANNominaIndividual()

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

    nomina.asignar_informacion_general(fe.nomina.InformacionGeneral(
        fecha_generacion = '2020-01-16',
        hora_generacion = '1053:10-05:00',
        tipo_ambiente = fe.nomina.InformacionGeneral.AMBIENTE_PRODUCCION,
        software_pin = '693',
        periodo_nomina = fe.nomina.PeriodoNomina(code='1'),
        tipo_moneda = fe.nomina.TipoMoneda(code='COP')
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

    nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
        dias_trabajados = 60,
        sueldo_trabajado = fe.nomina.Amount(3_500_000)
    ))

    nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
        porcentaje = fe.nomina.Amount(19),
        deduccion = fe.nomina.Amount(1_000_000)
    ))

    xml = nomina.toFachoXML()
    expected_cune = 'b8f9b6c24de07ffd92ea5467433a3b69357cfaffa7c19722db94b2e0eca41d057085a54f484b5da15ff585e773b0b0ab'
    assert xml.get_element_attribute('/nomina:NominaIndividual/InformacionGeneral', 'CUNE') == expected_cune
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/NumeroSecuenciaXML/@Numero') == 'N00001'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/NumeroSecuenciaXML/@Consecutivo') == '00001'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/LugarGeneracionXML/@Pais') == 'CO'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/LugarGeneracionXML/@DepartamentoEstado') == '05'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/LugarGeneracionXML/@MunicipioCiudad') == '05001'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/ProveedorXML/@NIT') == '999999'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/ProveedorXML/@DV') == '2'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/ProveedorXML/@SoftwareID') == 'xx'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/ProveedorXML/@SoftwareSC') is not None
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/CodigoQR') == f"https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={expected_cune}"
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/Empleador/@NIT') == '700085371'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/Trabajador/@NumeroDocumento') == '800199436'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/Novedad') == 'True'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividual/Novedad/@CUNENov') == 'N0111'

    # confirmar el namespace
    assert 'xmlns="dian:gov:co:facturaelectronica:NominaIndividual"' in xml.tostring()

def test_asignar_pago():
    nomina = fe.nomina.DIANNominaIndividual()
    nomina.asignar_pago(fe.nomina.Pago(
        forma = fe.nomina.FormaPago(code='1'),
        metodo = fe.nomina.MetodoPago(code='1')
    ))

def test_nomina_xmlsign(monkeypatch):
    nomina = fe.nomina.DIANNominaIndividual()
    xml = nomina.toFachoXML()

    signer = fe.nomina.DianXMLExtensionSigner('./tests/example.p12')
    xml.add_extension(signer)

    print(xml.tostring())
    elem = xml.get_element('/nomina:NominaIndividual/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature')
    assert elem is not None


def atest_nomina_ajuste_reemplazar():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    xml = nomina.toFachoXML()
    print(xml)
    assert False


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

    assert xml.get_element_text('/nomina:NominaIndividualDeAjuste/Reemplazar/ComprobanteTotal') == '1000000.00'


def test_adicionar_reemplazar_asignar_predecesor():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@NumeroPred') == '123456'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@CUNEPred') == 'ABC123456'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@FechaGenPred') == '2021-11-16'


def test_adicionar_reemplazar_eliminar_predecesor_opcional():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())

    assert xml.get_element('/nomina:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor') is not None
    assert xml.get_element('/nomina:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor') is None

def test_adicionar_eliminar_reemplazar_predecesor_opcional():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Eliminar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Eliminar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element('/nomina:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor') is not None
    assert xml.get_element('/nomina:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor') is None

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

    assert xml.get_element_text('/nomina:NominaIndividualDeAjuste/Eliminar/ComprobanteTotal') == '1000000.00'

def test_adicionar_eliminar_asignar_predecesor():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Eliminar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Eliminar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@NumeroPred') == '123456'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@CUNEPred') == 'ABC123456'
    assert xml.get_element_text_or_attribute('/nomina:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@FechaGenPred') == '2021-11-16'

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

def test_nomina_devengado_horas_extras_nocturnas():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoHorasExtrasNocturnas(
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
    extras = xml.get_element('/nomina:NominaIndividual/Devengados/HENs/HEN', multiple=True)
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

def test_nomina_devengado_horas_recargo_nocturno():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoHorasRecargoNocturno(
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
    extras = xml.get_element('/nomina:NominaIndividual/Devengados/HRNs/HRN', multiple=True)
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

def test_nomina_devengado_horas_extras_diarias_dominicales_y_festivos():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoHorasExtrasDiariasDominicalesYFestivos(
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
    extras = xml.get_element('/nomina:NominaIndividual/Devengados/HEDDFs/HEDDF', multiple=True)
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

def test_nomina_devengado_horas_recargo_diarias_dominicales_y_festivos():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoHorasRecargoDiariasDominicalesYFestivos(
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
    extras = xml.get_element('/nomina:NominaIndividual/Devengados/HRDDFs/HRDDF', multiple=True)
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


def test_nomina_devengado_horas_extras_nocturnas_dominicales_y_festivos():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoHorasExtrasNocturnasDominicalesYFestivos(
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
    extras = xml.get_element('/nomina:NominaIndividual/Devengados/HENDFs/HENDF', multiple=True)
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

def test_nomina_devengado_horas_recargo_nocturno_dominicales_y_festivos():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoHorasRecargoNocturnoDominicalesYFestivos(
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
    extras = xml.get_element('/nomina:NominaIndividual/Devengados/HRNDFs/HRNDF', multiple=True)
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

def test_fecha_validacion():
    with pytest.raises(ValueError) as e:
        fe.nomina.Fecha('535-35-3')
