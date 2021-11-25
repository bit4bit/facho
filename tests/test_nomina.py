#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

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

def test_nomina_xml():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.asignar_metadata(fe.nomina.Metadata(
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
            software_pin='12'
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
    # TODO(bit4bit) no logro generar cune igual al del anexo tecnico
    #assert xml.get_element_attribute('/fe:NominaIndividual/InformacionGeneral', 'CUNE') == '16560dc8956122e84ffb743c817fe7d494e058a44d9ca3fa4c234c268b4f766003253fbee7ea4af9682dd57210f3bac2'

    expected_cune = 'b8f9b6c24de07ffd92ea5467433a3b69357cfaffa7c19722db94b2e0eca41d057085a54f484b5da15ff585e773b0b0ab'
    assert xml.get_element_attribute('/fe:NominaIndividual/InformacionGeneral', 'fachoCUNE')  == "N000012020-01-161053:10-05:003500000.001000000.002500000.007000853718001994361026931"
    assert xml.get_element_attribute('/fe:NominaIndividual/InformacionGeneral', 'CUNE') == expected_cune
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/NumeroSecuenciaXML/@Numero') == 'N00001'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/NumeroSecuenciaXML/@Consecutivo') == '00001'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/LugarGeneracionXML/@Pais') == 'CO'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/LugarGeneracionXML/@DepartamentoEstado') == '05'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/LugarGeneracionXML/@MunicipioCiudad') == '05001'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/ProveedorXML/@NIT') == '999999'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/ProveedorXML/@DV') == '2'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/ProveedorXML/@SoftwareID') == 'xx'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/ProveedorXML/@fachoSoftwareSC') == 'xx12N00001'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/ProveedorXML/@SoftwareSC') is not None
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/CodigoQR') == f"https://catalogo‐vpfe-hab.dian.gov.co/document/searchqr?documentkey={expected_cune}"
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/Empleador/@NIT') == '700085371'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividual/Trabajador/@NumeroDocumento') == '800199436'

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
    with monkeypatch.context() as m:
        helpers.mock_urlopen(m)
        xml.add_extension(signer)

    print(xml.tostring())
    elem = xml.get_element('/fe:NominaIndividual/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature')
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

    assert xml.get_element_text('/fe:NominaIndividualDeAjuste/Reemplazar/ComprobanteTotal') == '1000000.00'


def test_adicionar_reemplazar_asignar_predecesor():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element_text_or_attribute('/fe:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@NumeroPred') == '123456'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@CUNEPred') == 'ABC123456'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor/@FechaGenPred') == '2021-11-16'


def test_adicionar_reemplazar_eliminar_predecesor_opcional():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())

    assert xml.get_element('/fe:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor') is not None
    assert xml.get_element('/fe:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor') is None

def test_adicionar_eliminar_reemplazar_predecesor_opcional():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Eliminar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Eliminar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element('/fe:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor') is not None
    assert xml.get_element('/fe:NominaIndividualDeAjuste/Reemplazar/ReemplazandoPredecesor') is None

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

    assert xml.get_element_text('/fe:NominaIndividualDeAjuste/Eliminar/ComprobanteTotal') == '1000000.00'

def test_adicionar_eliminar_asignar_predecesor():
    nomina = fe.nomina.DIANNominaIndividualDeAjuste.Eliminar()

    nomina.asignar_predecesor(fe.nomina.DIANNominaIndividualDeAjuste.Eliminar.Predecesor(
        numero = '123456',
        cune = 'ABC123456',
        fecha_generacion = '2021-11-16'
    ))

    xml = nomina.toFachoXML()
    print(xml.tostring())
    assert xml.get_element_text_or_attribute('/fe:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@NumeroPred') == '123456'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@CUNEPred') == 'ABC123456'
    assert xml.get_element_text_or_attribute('/fe:NominaIndividualDeAjuste/Eliminar/EliminandoPredecesor/@FechaGenPred') == '2021-11-16'


def test_fecha_validacion():
    with pytest.raises(ValueError) as e:
        fe.nomina.Fecha('535-35-3')
