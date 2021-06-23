#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest

import facho.model
import facho.model.fields as fields

def test_model_to_element():
    class Person(facho.model.Model):
        __name__ = 'Person'

    person = Person()

    assert "<Person/>" == person.to_xml()

def test_model_to_element_with_attribute():
    class Person(facho.model.Model):
        __name__ = 'Person'
        id = fields.Attribute('id')
        
    person = Person()
    person.id =  33

    personb = Person()
    personb.id = 44

    assert "<Person id=\"33\"/>" == person.to_xml()
    assert "<Person id=\"44\"/>" == personb.to_xml()

def test_model_to_element_with_attribute_as_element():
    class ID(facho.model.Model):
        __name__ = 'ID'

    class Person(facho.model.Model):
        __name__ = 'Person'
        
        id = fields.Many2One(ID)

    person = Person()
    person.id = 33
    assert "<Person><ID>33</ID></Person>" == person.to_xml()

def test_many2one_with_custom_attributes():
    class TaxAmount(facho.model.Model):
        __name__ = 'TaxAmount'

        currencyID = fields.Attribute('currencyID')
        
    class TaxTotal(facho.model.Model):
        __name__ = 'TaxTotal'

        amount = fields.Many2One(TaxAmount)

    tax_total = TaxTotal()
    tax_total.amount = 3333
    tax_total.amount.currencyID = 'COP'
    assert '<TaxTotal><TaxAmount currencyID="COP">3333</TaxAmount></TaxTotal>' == tax_total.to_xml()

def test_many2one_with_custom_setter():

    class PhysicalLocation(facho.model.Model):
        __name__ = 'PhysicalLocation'

        id = fields.Attribute('ID')
        
    class Party(facho.model.Model):
        __name__ = 'Party'

        location = fields.Many2One(PhysicalLocation, setter='location_setter')

        def location_setter(self, field, value):
            field.id = value
            
    party = Party()
    party.location = 99
    assert '<Party><PhysicalLocation ID="99"/></Party>' == party.to_xml()

def test_field_model():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Model(ID)

    person = Person()
    person.id = ID()
    person.id = 33
    assert "<Person><ID>33</ID></Person>" == person.to_xml()

def test_field_model_failed_initialization():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Model(ID)


    person = Person()
    person.id = 33
    assert "<Person><ID>33</ID></Person>" == person.to_xml()

def test_field_model_default_initialization_with_attributes():
    class ID(facho.model.Model):
        __name__ = 'ID'

        reference = fields.Attribute('REFERENCE')
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Model(ID)

    person = Person()
    person.id = 33
    person.id.reference = 'haber'
    assert '<Person><ID REFERENCE="haber">33</ID></Person>' == person.to_xml()

def test_model_with_xml_namespace():
    class Person(facho.model.Model):
        __name__ = 'Person'
        __namespace__ = {
            'facho': 'http://lib.facho.cyou'
        }

    person = Person()
    assert '<Person xmlns:facho="http://lib.facho.cyou"/>'

def test_model_with_xml_namespace_nested():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'
        __namespace__ = {
            'facho': 'http://lib.facho.cyou'
        }

        id = fields.Many2One(ID, namespace='facho')
        
    person = Person()
    person.id = 33
    assert '<Person xmlns:facho="http://lib.facho.cyou"><facho:ID>33</facho:ID></Person>' == person.to_xml()

def test_field_model_with_namespace():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'
        __namespace__ = {
            "facho": "http://lib.facho.cyou" 
        }
        id = fields.Model(ID, namespace="facho")


    person = Person()
    person.id = 33
    assert '<Person xmlns:facho="http://lib.facho.cyou"><facho:ID>33</facho:ID></Person>' == person.to_xml()
