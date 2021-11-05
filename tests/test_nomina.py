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

def test_adicionar_devengado_transporte():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_devengado(fe.nomina.DevengadoTransporte(
        auxilio_transporte = fe.nomina.Amount(2_000_000)
    ))

    xml = nomina.toFachoXML()

    assert xml.get_element_attribute('/fe:NominaIndividual/Devengados/Transporte', 'AuxilioTransporte') == '2000000.0'

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
    assert str(xml) == """<NominaIndividual xmlns:facho="http://git.disroot.org/Etrivial/facho" xmlns="http://www.dian.gov.co/contratos/facturaelectronica/v1" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cdt="urn:DocumentInformation:names:specification:ubl:colombia:schema:xsd:DocumentInformationAggregateComponents-1" xmlns:clm54217="urn:un:unece:uncefact:codelist:specification:54217:2001" xmlns:clmIANAMIMEMediaType="urn:un:unece:uncefact:codelist:specification:IANAMIMEMediaType:2003" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:sts="dian:gov:co:facturaelectronica:Structures-2-1" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:sig="http://www.w3.org/2000/09/xmldsig#"><Devengados><Basico/><Transporte AuxilioTransporte="2000000.0"/><Transporte AuxilioTransporte="3000000.0"/></Devengados><Deducciones/></NominaIndividual>"""


def test_adicionar_deduccion_salud():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
        porcentaje = fe.nomina.Amount(19),
        deduccion = fe.nomina.Amount(1000)
    ))

    xml = nomina.toFachoXML()
    print(xml)
    assert str(xml) == """<NominaIndividual xmlns:facho="http://git.disroot.org/Etrivial/facho" xmlns="http://www.dian.gov.co/contratos/facturaelectronica/v1" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cdt="urn:DocumentInformation:names:specification:ubl:colombia:schema:xsd:DocumentInformationAggregateComponents-1" xmlns:clm54217="urn:un:unece:uncefact:codelist:specification:54217:2001" xmlns:clmIANAMIMEMediaType="urn:un:unece:uncefact:codelist:specification:IANAMIMEMediaType:2003" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:qdt="urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2" xmlns:sts="dian:gov:co:facturaelectronica:Structures-2-1" xmlns:udt="urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:sig="http://www.w3.org/2000/09/xmldsig#"><Devengados><Basico/></Devengados><Deducciones><Salud Porcentaje="19.0" Deduccion="1000.0"/></Deducciones></NominaIndividual>"""

