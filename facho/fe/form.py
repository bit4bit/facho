# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import hashlib
from functools import reduce
import copy
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

from .data.dian import codelist
from . import fe


@dataclass
class Item:
    description: str
    id: str


@dataclass
class StandardItem(Item):
    pass


@dataclass
class Country:
    code: str
    name: str

@dataclass
class CountrySubentity:
    code: str
    name: str

@dataclass
class City:
    code: str
    name: str

@dataclass
class Address:
    name: str
    street: str = ''
    city: City = City('', '')
    country: Country = Country('CO', 'Colombia')
    countrysubentity: CountrySubentity = CountrySubentity('', '')

@dataclass
class PartyIdentification:
    number: str
    dv: str
    type_fiscal: str

    def __str__(self):
        return self.number

    def __eq__(self, other):
        return str(self) == str(other)

    def full(self):
        return "%s%s" % [self.number, self.dv]

@dataclass
class Responsability:
    codes: list

    def __str__(self):
        return ';'.join(self.codes)

    def __eq__(self, other):
        return str(self) == str(other)

    def __iter__(self):
        return iter(self.codes)


@dataclass
class Party:
    name: str
    ident: str
    responsability_code: str
    responsability_regime_code: str
    organization_code: str

    phone: str = ''
    address: Address = Address('')
    email: str = ''
    legal_name: str = ''
    legal_company_ident: str = ''
    legal_address: str = ''


@dataclass
class TaxSubTotal:
    percent: float
    tax_scheme_ident: str = '01'
    tax_scheme_name: str = 'IVA'

    tax_amount: float = 0.0
    taxable_amount: float = 0.0

    def calculate(self, invline):
        self.tax_amount = invline.total_amount * (self.percent / 100)
        self.taxable_amount = invline.total_amount


@dataclass
class TaxTotal:
    subtotals: list
    tax_amount: float = 0.0
    taxable_amount: float = 0.0

    def calculate(self, invline):
        for subtax in self.subtotals:
            subtax.calculate(invline)
            self.tax_amount += subtax.tax_amount
            self.taxable_amount += subtax.taxable_amount


@dataclass
class Price:
    amount: float
    type_code: str
    type: str


@dataclass
class PaymentMean:
    DEBIT = '01'
    CREDIT = '02'

    def __init__(self, id: str, code: str, due_at: datetime, payment_id: str):
        self.id = id
        self.code = code
        self.due_at = due_at
        self.payment_id = payment_id


@dataclass
class Payment:
    amount: float
    at: datetime

@dataclass
class PrePaidPayment(Payment):
    pass


@dataclass
class InvoiceLine:
    # RESOLUCION 0004: pagina 155
    quantity: int
    description: str
    item: Item
    price: Price
    # TODO mover a Invoice
    # ya que al reportar los totales es sobre
    # la factura y el percent es unico por type_code
    # de subtotal
    tax: TaxTotal

    @property
    def total_amount(self):
        return self.quantity * self.price.amount

    @property
    def total_tax_inclusive_amount(self):
        return self.tax.taxable_amount + self.tax.tax_amount

    @property
    def total_tax_exclusive_amount(self):
        return self.tax.taxable_amount

    @property
    def tax_amount(self):
        return self.tax.tax_amount

    @property
    def taxable_amount(self):
        return self.tax.taxable_amount

    def calculate(self):
        self.tax.calculate(self)


@dataclass
class LegalMonetaryTotal:
    line_extension_amount: float = 0.0
    tax_exclusive_amount: float = 0.0
    tax_inclusive_amount: float = 0.0
    charge_total_amount: float = 0.0
    payable_amount: float = 0.0

class Invoice:
    def __init__(self):
        self.invoice_period_start = None
        self.invoice_period_end = None
        self.invoice_issue = None
        self.invoice_ident = None
        self.invoice_operation_type = None
        self.invoice_legal_monetary_total = LegalMonetaryTotal(0, 0, 0, 0, 0)
        self.invoice_customer = None
        self.invoice_supplier = None
        self.invoice_payment_mean = None
        self.invoice_payments = []
        self.invoice_lines = []

    def set_period(self, startdate, enddate):
        self.invoice_period_start = startdate
        self.invoice_period_end = enddate

    def set_issue(self, dtime: datetime):
        self.invoice_issue = dtime

    def set_ident(self, ident: str):
        self.invoice_ident = ident

    def set_supplier(self, party: Party):
        self.invoice_supplier = party

    def set_customer(self, party: Party):
        self.invoice_customer = party

    def set_payment_mean(self, payment_mean: PaymentMean):
        self.invoice_payment_mean = payment_mean

    def set_operation_type(self, operation):
        self.invoice_operation_type = operation

    def add_invoice_line(self, line: InvoiceLine):
        self.invoice_lines.append(line)

    def accept(self, visitor):
        visitor.visit_payment_mean(self.invoice_payment_mean)
        visitor.visit_customer(self.invoice_customer)
        visitor.visit_supplier(self.invoice_supplier)
        for payment in self.invoice_payments:
            visitor.visit_payment(payment)
        for invline in self.invoice_lines:
            visitor.visit_invoice_line(invline)

    def _calculate_legal_monetary_total(self):
        for invline in self.invoice_lines:
            self.invoice_legal_monetary_total.line_extension_amount += invline.total_amount
            self.invoice_legal_monetary_total.tax_exclusive_amount += invline.total_tax_exclusive_amount
            #DIAN 1.7.-2020: FAU6
            self.invoice_legal_monetary_total.tax_inclusive_amount += invline.total_tax_inclusive_amount


        #DIAN 1.7.-2020: FAU10
        # se omite revisar como implementar el booleano
        self.invoice_legal_monetary_total.charge_total_amount = 0

        #DIAN 1.7.-2020: FAU14 parcial
        self.invoice_legal_monetary_total.payable_amount = self.invoice_legal_monetary_total.tax_inclusive_amount + self.invoice_legal_monetary_total.charge_total_amount

    def calculate(self):
        for invline in self.invoice_lines:
            invline.calculate()
        self._calculate_legal_monetary_total()


class DianResolucion0001Validator:

    def __init__(self):
        self.errors = []

    def _validate_party(self, model, party):
        for code in party.responsability_code:
            if code not in codelist.TipoResponsabilidad:
                self.errors.append((model,
                                    'responsability_code',
                                    'not found %s' % (code)))

        try:
            codelist.TipoOrganizacion[party.organization_code]
        except KeyError:
            self.errors.append((model, 'organization_code' ,
                                'not found %s' % (party.organization_code)))
        try:
            codelist.Departamento[party.address.countrysubentity.code]
        except KeyError:
            self.errors.append((model, 'countrysubentity_code',
                                'not found %s' % (party.address.countrysubentity.code)))
        try:
            codelist.Municipio[party.address.city.code]
        except KeyError:
            self.errors.append((model, 'city_code',
                                'not found %s' % (party.address.city.code)))

    def _validate_invoice(self, invoice):
        try:
            codelist.TipoOperacionF[invoice.invoice_operation_type]
        except KeyError:
            self.errors.append(('invoice', 'operation_type',
                                'not found %s' % (invoice.invoice_operation_type)))

        # MACHETE se espera en zona horario colombia
        if invoice.invoice_issue.tzname() not in ['UTC-05:00', '-05', None]:
            self.errors.append(('invoice', 'invoice_issue',
                                'expected timezone UTC-05:00 or -05 or empty got %s' % (invoice.invoice_issue.tzname())))

    def validate(self, invoice):
        invoice.accept(self)
        self._validate_invoice(invoice)

        return not self.errors

    def visit_payment_mean(self, mean):
        try:
            codelist.MediosPago[mean.code]
        except KeyError:
            self.errors.append(('payment_mean', 'code',
                                'not found %s' % (mean.code)))

    def visit_customer(self, customer):
        self._validate_party('customer', customer)

    def visit_supplier(self, supplier):
        self._validate_party('supplier', supplier)

    def visit_payment(self, payment):
        pass

    def visit_invoice_line(self, line):
        try:
            codelist.CodigoPrecioReferencia[line.price.type_code]
        except KeyError:
            self.errors.append(('invoice_line', 'line.price',
                               'not found %s' % (line.price.type_code)))

    def valid(self):
        return not self.errors


class DIANInvoiceXML(fe.FeXML):
    """
    DianInvoiceXML mapea objeto form.Invoice a XML segun
    lo indicado para la facturacion electronica.
    """

    def __init__(self, invoice):
        super().__init__('Invoice', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')
        self.placeholder_for('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')

        # ZE02 se requiere existencia para firmar
        ublextension = self.fragment('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension', append=True)
        extcontent = ublextension.find_or_create_element('/ext:UBLExtension/ext:ExtensionContent')
        self.attach_invoice(invoice)

    def set_supplier(fexml, invoice):
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty')
        #DIAN 1.7.-2020: FAJ02
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cbc:AdditionalAccountID',
                          invoice.invoice_supplier.organization_code)
        #DIAN 1.7.-2020: FAJ06
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_supplier.name)
        #DIAN 1.7.-2020: FAJ07
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address')
        #DIAN 1.7.-2020: FAJ08
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: FAJ09
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName',
                          invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: FAJ11
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)
        #DIAN 1.7.-2020: FAJ12
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: FAJ14
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)
        #DIAN 1.7.-2020: FAJ16
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)

        supplier_address_id_attrs = {'languageID' : 'es'}
        #DIAN 1.7.-2020: FAJ17
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                         #DIAN 1.7.-2020: FAJ18
                         **supplier_address_id_attrs)

        supplier_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        supplier_company_id_attrs.update({'schemeID': invoice.invoice_supplier.ident.dv,
                                          'schemeName': invoice.invoice_supplier.ident.type_fiscal})

        #DIAN 1.7.-2020: FAJ19
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme')
        #DIAN 1.7.-2020: FAJ20
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        #DIAN 1.7.-2020: FAJ21
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          #DIAN 1.7.-2020: FAJ22,FAJ23,FAJ24,FAJ25
                          **supplier_company_id_attrs)
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          #DIAN 1.7.-2020: FAJ26
                          invoice.invoice_supplier.responsability_code,
                          #DIAN 1.7.-2020: FAJ27
                          listName=invoice.invoice_supplier.responsability_regime_code)
        #DIAN 1.7.-2020: FAJ28
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')
        #DIAN 1.7.-2020: FAJ29
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: FAJ30
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName', invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: FAJ31
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)
        #DIAN 1.7.-2020: FAJ32
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: FAJ33,FAJ34
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)
        #DIAN 1.7.-2020: FAJ35,FAJ36
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)
        supplier_address_id_attrs = {'languageID' : 'es'}
        #DIAN 1.7.-2020: FAJ37,FAJ38
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                          **supplier_address_id_attrs)
        #DIAN 1.7.-2020: FAJ39
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')

        #DIAN 1.7.-2020: FAJ42
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: FAJ43
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        #DIAN 1.7.-2020: FAJ44,FAJ45,FAJ46,FAJ47,FAJ48
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          **supplier_company_id_attrs)
        #DIAN 1.7.-2020: FAJ49
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme')
        #DIAN 1.7.-2020: FAJ50
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme/cbc:ID',
                          'SETP')
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact')
        #DIAN 1.7.-2020: FAJ71
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_supplier.email)


    def set_customer(fexml, invoice):
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty')
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cbc:AdditionalAccountID',
                          invoice.invoice_customer.organization_code)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID',
                          invoice.invoice_customer.ident)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_customer.name)

        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation')
        customer_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        #DIAN 1.7.-2020: FAK25
        customer_company_id_attrs.update({'schemeID': invoice.invoice_customer.ident.dv,
                                          'schemeName': invoice.invoice_customer.ident.type_fiscal})
        #DIAN 1.7.-2020: FAK07
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address')
        #DIAN 1.7.-2020: FAK08
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: FAK09
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName', invoice.invoice_customer.address.city.name)
        #DIAN 1.7.-2020: FAK11
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)
        #DIAN 1.7.-2020: FAK12
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)
        #DIAN 1.7.-2020: FAK16
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)
        customer_address_id_attrs = {'languageID' : 'es'}
        #DIAN 1.7.-2020: FAK17
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_customer.address.country.name,
                         #DIAN 1.7.-2020: FAK18
                         **customer_address_id_attrs)
        #DIAN 1.7.-2020: FAK17,FAK19
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme')
        #DIAN 1.7.-2020: FAK17,FAK20
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        #DIAN 1.7.-2020: FAK21
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          **customer_company_id_attrs)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          #DIAN 1.7.-2020: FAK26
                          invoice.invoice_customer.responsability_code,
                          #DIAN 1.7.-2020: FAK27
                          listName=invoice.invoice_customer.responsability_regime_code)
        #DIAN 1.7.-2020: FAK28
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')
        #DIAN 1.7.-2020: FAK29
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: FAK30
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName',
                          invoice.invoice_customer.address.city.name)
        #DIAN 1.7.-2020: FAK31
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)
        #DIAN 1.7.-2020: FAK32
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)
        #DIAN 1.7.-2020: FAK33
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine')
        #DIAN 1.7.-2020: FAK34
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)
        #DIAN 1.7.-2020: FAK35
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country')
        #DIAN 1.7.-2020: FAK36
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)
        #DIAN 1.7.-2020: FAK37
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name', invoice.invoice_customer.address.country.name)
        #DIAN 1.7.-2020: FAK38
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code,
                          **customer_address_id_attrs)
        #DIAN 1.7.-2020: FAK39
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')
        #DIAN 1.7.-2020: FAK40 Machete Construir Validación
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          'ZY')
        #DIAN 1.7.-2020: FAK41 Machete Construir Validación
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          'No causa')
        #DIAN 1.7.-2020: FAK42
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: FAK43
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        #DIAN 1.7.-2020: FAK44,FAK45,FAK46,FAK47,FAK48
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          **customer_company_id_attrs)
        #DIAN 1.7.-2020: FAK51
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: FAK55
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_customer.email)

    def set_payment_mean(fexml, invoice):
        payment_mean = invoice.invoice_payment_mean
        fexml.set_element('/fe:Invoice/cac:PaymentMeans/cbc:ID', payment_mean.id)
        fexml.set_element('/fe:Invoice/cac:PaymentMeans/cbc:PaymentMeansCode', payment_mean.code)
        fexml.set_element('/fe:Invoice/cac:PaymentMeans/cbc:PaymentDueDate', payment_mean.due_at.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:Invoice/cac:PaymentMeans/cbc:PaymentID', payment_mean.payment_id)

    def set_legal_monetary(fexml, invoice):
        fexml.set_element('/fe:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount',
                          #MACHETE redondeo en valor
                          '%.02f' % (invoice.invoice_legal_monetary_total.line_extension_amount),
                          currencyID='COP')
        fexml.set_element('/fe:Invoice/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount',
                          #MACHETE redondeo en valor
                          '%.02f' % (invoice.invoice_legal_monetary_total.tax_exclusive_amount),
                          currencyID='COP')
        fexml.set_element('/fe:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount',
                          #MACHETE ...
                          '%.02f' % (invoice.invoice_legal_monetary_total.tax_inclusive_amount),
                          currencyID='COP')
        fexml.set_element('/fe:Invoice/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount',
                          #MACHETE ...
                          '%.02f' % (invoice.invoice_legal_monetary_total.charge_total_amount),
                          currencyID='COP')
        fexml.set_element('/fe:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount',
                          #MACHETE ...
                          '%.02f' % (invoice.invoice_legal_monetary_total.payable_amount),
                          currencyID='COP')

    def set_invoice_totals(fexml, invoice):
        tax_amount_for = defaultdict(lambda: defaultdict(lambda: 0.0))
        percent_for = defaultdict(lambda: None)

        #requeridos para CUFE
        tax_amount_for['01']['tax_amount'] = 0.0
        tax_amount_for['01']['taxable_amount'] = 0.0
        #DIAN 1.7.-2020: FAS07 => Se debe construir estrategia para  su manejo
        #tax_amount_for['04']['tax_amount'] = 0.0
        #tax_amount_for['04']['taxable_amount'] = 0.0
        #tax_amount_for['03']['tax_amount'] = 0.0
        #tax_amount_for['03']['taxable_amount'] = 0.0

        total_tax_amount = 0.0

        for invoice_line in invoice.invoice_lines:
            for subtotal in invoice_line.tax.subtotals:
                tax_amount_for[subtotal.tax_scheme_ident]['tax_amount'] += subtotal.tax_amount
                tax_amount_for[subtotal.tax_scheme_ident]['taxable_amount'] += subtotal.taxable_amount
                total_tax_amount += subtotal.tax_amount
                # MACHETE ojo InvoiceLine.tax pasar a Invoice
                percent_for[subtotal.tax_scheme_ident] = subtotal.percent

        fexml.placeholder_for('/fe:Invoice/cac:TaxTotal')
        fexml.set_element('/fe:Invoice/cac:TaxTotal/cbc:TaxAmount', total_tax_amount,
                          currencyID='COP')

        for index, item in enumerate(tax_amount_for.items()):
            cod_impuesto, amount_of = item
            next_append = index > 0

            #DIAN 1.7.-2020: FAS01
            line = fexml.fragment('/fe:Invoice/cac:TaxTotal', append=next_append)

            #DIAN 1.7.-2020: FAU06
            tax_amount = amount_of['tax_amount']
            line.set_element('/cac:TaxTotal/cbc:TaxAmount',
                             # MACHETE
                             '%.02f' % (tax_amount), currencyID='COP')

            #DIAN 1.7.-2020: FAS05
            line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount',
                             # MACHETE
                             '%.02f' % (amount_of['taxable_amount']), currencyID='COP')

            #DIAN 1.7.-2020: FAU06
            line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount',
                             # MACHETE
                             '%.02f' % (amount_of['tax_amount']), currencyID='COP')

            #DIAN 1.7.-2020: FAS07
            if percent_for[cod_impuesto]:
                line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cbc:Percent',
                                 percent_for[cod_impuesto])


            if percent_for[cod_impuesto]:
                line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent',
                                 percent_for[cod_impuesto])
            line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID',
                             cod_impuesto)


    def set_invoice_lines(fexml, invoice):
        next_append = False
        for index, invoice_line in enumerate(invoice.invoice_lines):
            line = fexml.fragment('/fe:Invoice/cac:InvoiceLine', append=next_append)
            next_append = True

            line.set_element('/cac:InvoiceLine/cbc:ID', index + 1)
            line.set_element('/cac:InvoiceLine/cbc:InvoicedQuantity', invoice_line.quantity, unitCode = 'NAR')
            line.set_element('/cac:InvoiceLine/cbc:LineExtensionAmount', invoice_line.total_amount, currencyID="COP")
            line.set_element('/cac:InvoiceLine/cac:TaxTotal/cbc:TaxAmount', invoice_line.tax_amount, currencyID='COP')

            #condition_price = line.fragment('/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice')
            #condition_price.set_element('/cac:AlternativeConditionPrice/cbc:PriceAmount', invoice_line.price.amount, currencyID='COP')
            #condition_price.set_element('/cac:AlternativeConditionPrice/cbc:PriceTypeCode', invoice_line.price.type_code)
            #condition_price.set_element('/cac:AlternativeConditionPrice/cbc:PriceType', invoice_line.price.type)

            for subtotal in invoice_line.tax.subtotals:
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount', subtotal.taxable_amount, currencyID='COP')
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount', subtotal.tax_amount, currencyID='COP')
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent', subtotal.percent)
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID', subtotal.tax_scheme_ident)
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name', subtotal.tax_scheme_name)
            line.set_element('/cac:InvoiceLine/cac:Item/cbc:Description', invoice_line.item.description)
            # TODO
            line.set_element('/cac:InvoiceLine/cac:Item/cac:StandardItemIdentification/cbc:ID', invoice_line.item.id)
            line.set_element('/cac:InvoiceLine/cac:Price/cbc:PriceAmount', invoice_line.price.amount, currencyID="COP")
            #DIAN 1.7.-2020: FBB04
            line.set_element('/cac:InvoiceLine/cac:Price/cbc:BaseQuantity', invoice_line.price.amount)

    def attach_invoice(fexml, invoice):
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""

        fexml.placeholder_for('/fe:Invoice/ext:UBLExtensions')
        fexml.set_element('/fe:Invoice/cbc:UBLVersionID', 'UBL 2.1')
        fexml.set_element('/fe:Invoice/cbc:CustomizationID', invoice.invoice_operation_type)
        fexml.placeholder_for('/fe:Invoice/cbc:ProfileID')
        fexml.placeholder_for('/fe:Invoice/cbc:ProfileExecutionID')
        fexml.set_element('/fe:Invoice/cbc:ID', invoice.invoice_ident)
        fexml.placeholder_for('/fe:Invoice/cbc:UUID')
        fexml.set_element('/fe:Invoice/cbc:DocumentCurrencyCode', 'COP')
        fexml.set_element('/fe:Invoice/cbc:IssueDate', invoice.invoice_issue.strftime('%Y-%m-%d'))
        #DIAN 1.7.-2020: FAD10
        fexml.set_element('/fe:Invoice/cbc:IssueTime', invoice.invoice_issue.strftime('%H:%M:%S-05:00'))
        fexml.set_element('/fe:Invoice/cbc:InvoiceTypeCode', codelist.TipoDocumento.by_name('Factura de Venta Nacional')['code'],
                          listAgencyID='195',
                          listAgencyName='No matching global declaration available for the validation root',
                          listURI='http://www.dian.gov.co')
        fexml.set_element('/fe:Invoice/cbc:LineCountNumeric', len(invoice.invoice_lines))
        fexml.set_element('/fe:Invoice/cac:InvoicePeriod/cbc:StartDate', invoice.invoice_period_start.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:Invoice/cac:InvoicePeriod/cbc:EndDate', invoice.invoice_period_end.strftime('%Y-%m-%d'))

        fexml.set_supplier(invoice)
        fexml.set_customer(invoice)
        fexml.set_legal_monetary(invoice)
        fexml.set_invoice_totals(invoice)
        fexml.set_invoice_lines(invoice)
        fexml.set_payment_mean(invoice)

        return fexml
