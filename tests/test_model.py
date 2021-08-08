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

def test_many2one_always_create():
    class Name(facho.model.Model):
        __name__ = 'Name'

    class Person(facho.model.Model):
        __name__ = 'Person'

        name = fields.Many2One(Name, default='facho')

    person = Person()
    assert '<Person><Name>facho</Name></Person>' == person.to_xml()

def test_many2one_nested_always_create():
    class Name(facho.model.Model):
        __name__ = 'Name'

    class Contact(facho.model.Model):
        __name__ = 'Contact'

        name = fields.Many2One(Name, default='facho')
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        contact = fields.Many2One(Contact, create=True)

    person = Person()
    assert '<Person><Contact><Name>facho</Name></Contact></Person>' == person.to_xml()

def test_many2one_auto_create():
    class TaxAmount(facho.model.Model):
        __name__ = 'TaxAmount'

        currencyID = fields.Attribute('currencyID')
        
    class TaxTotal(facho.model.Model):
        __name__ = 'TaxTotal'

        amount = fields.Many2One(TaxAmount)

    tax_total = TaxTotal()
    tax_total.amount.currencyID = 'COP'
    tax_total.amount = 3333
    assert '<TaxTotal><TaxAmount currencyID="COP">3333</TaxAmount></TaxTotal>' == tax_total.to_xml()

def test_field_model():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Many2One(ID)

    person = Person()
    person.id = ID()
    person.id = 33
    assert "<Person><ID>33</ID></Person>" == person.to_xml()

def test_field_multiple_model():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Many2One(ID)
        id2 = fields.Many2One(ID)

    person = Person()
    person.id = 33
    person.id2 = 44
    assert "<Person><ID>33</ID><ID>44</ID></Person>" == person.to_xml()

def test_field_model_failed_initialization():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Many2One(ID)


    person = Person()
    person.id = 33
    assert "<Person><ID>33</ID></Person>" == person.to_xml()

def test_field_model_with_custom_name():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Many2One(ID, name='DID')


    person = Person()
    person.id = 33
    assert "<Person><DID>33</DID></Person>" == person.to_xml()

def test_field_model_default_initialization_with_attributes():
    class ID(facho.model.Model):
        __name__ = 'ID'

        reference = fields.Attribute('REFERENCE')
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Many2One(ID)

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

def test_model_with_xml_namespace_nested_nested():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Party(facho.model.Model):
        __name__ = 'Party'

        id = fields.Many2One(ID, namespace='party')

        def __default_set__(self, value):
            self.id = value

    class Person(facho.model.Model):
        __name__ = 'Person'
        __namespace__ = {
            'person': 'http://lib.facho.cyou',
            'party': 'http://lib.facho.cyou'
        }

        id = fields.Many2One(Party, namespace='person')
        
    person = Person()
    person.id = 33
    assert '<Person xmlns:person="http://lib.facho.cyou" xmlns:party="http://lib.facho.cyou"><person:Party><party:ID>33</party:ID></person:Party></Person>' == person.to_xml()

def test_model_with_xml_namespace_nested_one_many():
    class Name(facho.model.Model):
        __name__ = 'Name'

    class Contact(facho.model.Model):
        __name__ = 'Contact'

        name = fields.Many2One(Name, namespace='contact')

    class Person(facho.model.Model):
        __name__ = 'Person'
        __namespace__ = {
            'facho': 'http://lib.facho.cyou',
            'contact': 'http://lib.facho.cyou'
        }

        contacts = fields.One2Many(Contact, namespace='facho')
        
    person = Person()
    contact = person.contacts.create()
    contact.name = 'contact1'

    contact = person.contacts.create()
    contact.name = 'contact2'

    assert '<Person xmlns:facho="http://lib.facho.cyou" xmlns:contact="http://lib.facho.cyou"><facho:Contact><contact:Name>contact1</contact:Name></facho:Contact><facho:Contact><contact:Name>contact2</contact:Name></facho:Contact></Person>' == person.to_xml()

def test_field_model_with_namespace():
    class ID(facho.model.Model):
        __name__ = 'ID'
        
    class Person(facho.model.Model):
        __name__ = 'Person'
        __namespace__ = {
            "facho": "http://lib.facho.cyou" 
        }
        id = fields.Many2One(ID, namespace="facho")


    person = Person()
    person.id = 33
    assert '<Person xmlns:facho="http://lib.facho.cyou"><facho:ID>33</facho:ID></Person>' == person.to_xml()

def test_field_hook_before_xml():
    class Hash(facho.model.Model):
        __name__ = 'Hash'
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        hash = fields.Many2One(Hash)

        def __before_xml__(self):
            self.hash = "calculate"
            
    person = Person()
    assert "<Person><Hash>calculate</Hash></Person>" == person.to_xml()


def test_field_function_with_attribute():
    class Person(facho.model.Model):
        __name__ = 'Person'

        hash = fields.Function(fields.Attribute('hash'), getter='get_hash')

        def get_hash(self, name, field):
            return 'calculate'
        
    person = Person()
    assert '<Person hash="calculate"/>'

def test_field_function_with_model():
    class Hash(facho.model.Model):
        __name__ = 'Hash'

        id = fields.Attribute('id')
        
    class Person(facho.model.Model):
        __name__ = 'Person'

        hash = fields.Function(fields.Many2One(Hash), getter='get_hash')

        def get_hash(self, name, field):
            field.id = 'calculate'

        
    person = Person()
    assert person.hash.id == 'calculate'
    assert '<Person/>'
   

def test_field_function_setter():
    class Person(facho.model.Model):
        __name__ = 'Person'

        hash = fields.Attribute('hash')
        password = fields.Virtual(setter='set_hash')

        def set_hash(self, name, value):
            self.hash = "%s+2" % (value)

    person = Person()
    person.password = 'calculate'
    assert '<Person hash="calculate+2"/>' == person.to_xml()

def test_field_function_only_setter():
    class Person(facho.model.Model):
        __name__ = 'Person'

        hash = fields.Attribute('hash')
        password = fields.Virtual(setter='set_hash')

        def set_hash(self, name, value):
            self.hash = "%s+2" % (value)

    person = Person()
    person.password = 'calculate'
    assert '<Person hash="calculate+2"/>' == person.to_xml()
    
def test_model_set_default_setter():
    class Hash(facho.model.Model):
        __name__ = 'Hash'

        def __default_set__(self, value):
            return "%s+3" % (value)

    class Person(facho.model.Model):
        __name__ = 'Person'

        hash = fields.Many2One(Hash)

    person = Person()
    person.hash = 'hola'
    assert '<Person><Hash>hola+3</Hash></Person>' == person.to_xml()


def test_field_virtual():
    class Person(facho.model.Model):
        __name__ = 'Person'

        age = fields.Virtual()

    person = Person()
    person.age = 55
    assert person.age == 55
    assert "<Person/>" == person.to_xml()


def test_field_inserted_default_attribute():
    class Person(facho.model.Model):
        __name__ = 'Person'

        hash = fields.Attribute('hash', default='calculate')


    person = Person()
    assert '<Person hash="calculate"/>' == person.to_xml()

def test_field_function_inserted_default_attribute():
    class Person(facho.model.Model):
        __name__ = 'Person'

        hash = fields.Function(fields.Attribute('hash'), default='calculate')

    person = Person()
    assert '<Person hash="calculate"/>' == person.to_xml()

def test_field_inserted_default_many2one():
    class ID(facho.model.Model):
        __name__ = 'ID'

        key = fields.Attribute('key')
        
        def __default_set__(self, value):
            self.key = value

    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Many2One(ID, default="oe")

    person = Person()
    assert '<Person><ID key="oe"/></Person>' == person.to_xml()

def test_field_inserted_default_nested_many2one():
    class ID(facho.model.Model):
        __name__ = 'ID'

    class Person(facho.model.Model):
        __name__ = 'Person'

        id = fields.Many2One(ID, default="ole")

    person = Person()
    assert '<Person><ID>ole</ID></Person>' == person.to_xml()

def test_model_on_change_field():
    class Hash(facho.model.Model):
        __name__ = 'Hash'

    class Person(facho.model.Model):
        __name__ = 'Person'

        react = fields.Attribute('react')
        hash = fields.Many2One(Hash)

        @fields.on_change(['hash'])
        def on_change_react(self, name, value):
            assert name == 'hash'
            self.react = "%s+4" % (value)

    person = Person()
    person.hash = 'hola'
    assert '<Person react="hola+4"><Hash>hola</Hash></Person>' == person.to_xml()

def test_model_on_change_field_attribute():
    class Person(facho.model.Model):
        __name__ = 'Person'

        react = fields.Attribute('react')
        hash = fields.Attribute('Hash')

        @fields.on_change(['hash'])
        def on_react(self, name, value):
            assert name == 'hash'
            self.react = "%s+4" % (value)

    person = Person()
    person.hash = 'hola'
    assert '<Person react="hola+4" Hash="hola"/>' == person.to_xml()

def test_model_one2many():
    class Line(facho.model.Model):
        __name__ = 'Line'

        quantity = fields.Attribute('quantity')
        
    class Invoice(facho.model.Model):
        __name__ = 'Invoice'

        lines = fields.One2Many(Line)

    invoice = Invoice()
    line = invoice.lines.create()
    line.quantity = 3
    line = invoice.lines.create()
    line.quantity = 5
    assert '<Invoice><Line quantity="3"/><Line quantity="5"/></Invoice>' == invoice.to_xml()


def test_model_one2many_with_on_changes():
    class Line(facho.model.Model):
        __name__ = 'Line'

        quantity = fields.Attribute('quantity')
        
    class Invoice(facho.model.Model):
        __name__ = 'Invoice'

        lines = fields.One2Many(Line)
        count = fields.Attribute('count', default=0)
        
        @fields.on_change(['lines'])
        def refresh_count(self, name, value):
            self.count = len(self.lines)

    invoice = Invoice()
    line = invoice.lines.create()
    line.quantity = 3
    line = invoice.lines.create()
    line.quantity = 5

    assert len(invoice.lines) == 2
    assert '<Invoice count="2"><Line quantity="3"/><Line quantity="5"/></Invoice>' == invoice.to_xml()

def test_model_one2many_as_list():
    class Line(facho.model.Model):
        __name__ = 'Line'

        quantity = fields.Attribute('quantity')
        
    class Invoice(facho.model.Model):
        __name__ = 'Invoice'

        lines = fields.One2Many(Line)

    invoice = Invoice()
    line = invoice.lines.create()
    line.quantity = 3
    line = invoice.lines.create()
    line.quantity = 5

    lines = list(invoice.lines)
    assert len(list(invoice.lines)) == 2

    for line in lines:
        assert isinstance(line, Line)
    assert '<Invoice><Line quantity="3"/><Line quantity="5"/></Invoice>' == invoice.to_xml()


def test_model_attributes_order():
    class Line(facho.model.Model):
        __name__ = 'Line'

        quantity = fields.Attribute('quantity')
        
    class Invoice(facho.model.Model):
        __name__ = 'Invoice'

        line1 = fields.Many2One(Line, name='Line1')
        line2 = fields.Many2One(Line, name='Line2')
        line3 = fields.Many2One(Line, name='Line3')


    invoice = Invoice()
    invoice.line2.quantity = 2
    invoice.line3.quantity = 3
    invoice.line1.quantity = 1

    assert '<Invoice><Line1 quantity="1"/><Line2 quantity="2"/><Line3 quantity="3"/></Invoice>' == invoice.to_xml()


def test_field_amount():
    class Line(facho.model.Model):
        __name__ = 'Line'

        amount = fields.Amount(name='Amount', precision=1)
        amount_as_attribute = fields.Attribute('amount')

        @fields.on_change(['amount'])
        def on_amount(self, name, value):
            self.amount_as_attribute = self.amount

    line = Line()
    line.amount = 33

    assert '<Line amount="33.0"/>' == line.to_xml()
        

def test_model_setup():
    class Line(facho.model.Model):
        __name__ = 'Line'

        amount = fields.Attribute(name='amount')

        def __setup__(self):
            self.amount = 23

    line = Line()
    assert '<Line amount="23"/>' == line.to_xml()
