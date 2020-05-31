# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import hashlib
from functools import reduce
import copy
from dataclasses import dataclass
from datetime import datetime

from .data.dian import codelist
from . import fe

@dataclass
class Party:
    name: str
    ident: str
    responsability_code: str
    organization_code: str

    phone: str = ''
    address: str = ''
    email: str = ''
    legal_name: str = ''
    legal_company_ident: str = ''
    legal_address: str = ''



@dataclass
class TaxSubTotal:
    percent: float
    tax_scheme_ident: str = '01'

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
class InvoiceLine:
    # RESOLUCION 0004: pagina 155
    quantity: int
    description: str
    item_ident: int
    price_amount: float
    tax: TaxTotal

    @property
    def total_amount(self):
        return self.quantity * self.price_amount

    @property
    def total_tax_inclusive_amount(self):
        return self.tax.taxable_amount + self.tax.tax_amount

    @property
    def total_tax_exclusive_amount(self):
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
        self.invoice_legal_monetary_total = LegalMonetaryTotal(0, 0, 0, 0, 0)
        self.invoice_customer = None
        self.invoice_supplier = None
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

    def add_invoice_line(self, line: InvoiceLine):
        self.invoice_lines.append(line)

    def accept(self, visitor):
        visitor.visit_customer(self.invoice_customer)
        visitor.visit_supplier(self.invoice_supplier)
        for invline in self.invoice_lines:
            visitor.visit_invoice_line(invline)

    def _calculate_legal_monetary_total(self):
        for invline in self.invoice_lines:
            self.invoice_legal_monetary_total.line_extension_amount += invline.total_amount
            self.invoice_legal_monetary_total.tax_exclusive_amount += invline.total_tax_exclusive_amount
            self.invoice_legal_monetary_total.tax_inclusive_amount += invline.total_tax_inclusive_amount
            self.invoice_legal_monetary_total.charge_total_amount += invline.total_amount
        #self.invoice_legal_monetary_total.payable_amount = self.invoice_legal_monetary_total.tax_exclusive_amount \
        #    + self.invoice_legal_monetary_total.line_extension_amount \
        #    + self.invoice_legal_monetary_total.tax_inclusive_amount
        self.invoice_legal_monetary_total.payable_amount = self.invoice_legal_monetary_total.tax_inclusive_amount
        
    def calculate(self):
        for invline in self.invoice_lines:
            invline.calculate()
        self._calculate_legal_monetary_total()


class DianResolucion0001Validator:

    def __init__(self):
        self.errors = []

    def _validate_party(self, party):
        try:
            codelist.TipoResponsabilidad[party.responsability_code]
        except KeyError:
            self.errors.append(('responsability_code', 'not found'))

        try:
            codelist.TipoOrganizacion[party.organization_code]
        except KeyError:
            self.errors.append(('organization_code', 'not found'))

    def validate(self, invoice):
        invoice.accept(self)
        return not self.errors

    def visit_customer(self, customer):
        self._validate_party(customer)

    def visit_supplier(self, supplier):
        self._validate_party(supplier)

    def visit_invoice_line(self, line):
        pass

    def valid(self):
        return not self.errors


class DIANInvoiceXML(fe.FeXML):

    def __init__(self, invoice):
        super().__init__('Invoice', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')
        self.attach_invoice(invoice)

    def attach_invoice(self, invoice):
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""
        fexml = self

        invoice.calculate()

        fexml.set_element('/fe:Invoice/cbc:UBLVersionID', 'UBL 2.1')
        fexml.set_element('/fe:Invoice/cbc:ID', invoice.invoice_ident)
        fexml.set_element('/fe:Invoice/cbc:IssueDate', invoice.invoice_issue.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:Invoice/cbc:IssueTime', invoice.invoice_issue.strftime('%H:%M:%S%z'))
        fexml.set_element('/fe:Invoice/cac:InvoicePeriod/cbc:StartDate', invoice.invoice_period_start.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:Invoice/cac:InvoicePeriod/cbc:EndDate', invoice.invoice_period_end.strftime('%Y-%m-%d'))

        fexml.set_element('/fe:Invoice/cbc:LineCountNumeric', len(invoice.invoice_lines))

        fexml.set_element('/fe:Invoice/fe:AccountingSupplierParty/fe:Party/cac:PartyIdentification/cbc:ID',
                          invoice.invoice_supplier.ident)
        fexml.set_element('/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_supplier.ident)
        fexml.set_element('/fe:Invoice/fe:AccountingSupplierParty/fe:Party/fe:PartyTaxScheme/cbc:TaxLevelCode',
                          invoice.invoice_supplier.responsability_code)
        fexml.set_element('/fe:Invoice/fe:AccountingSupplierParty/cbc:AdditionalAccountID',
                          invoice.invoice_supplier.organization_code)
        fexml.set_element('/fe:Invoice/fe:AccountingSupplierParty/fe:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_supplier.name)
        fexml.set_element('/fe:Invoice/fe:AccountingSupplierParty/fe:Party/fe:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        fexml.set_element('/fe:Invoice/fe:AccountingSupplierParty/fe:Party/fe:PhysicalLocation/fe:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address)
        fexml.set_element('/fe:Invoice/fe:AccountingCustomerParty/fe:Party/cac:PartyIdentification/cbc:ID',
                          invoice.invoice_customer.ident)
        fexml.set_element('/fe:Invoice/fe:AccountingCustomerParty/fe:Party/fe:PartyTaxScheme/cbc:TaxLevelCode',
                          invoice.invoice_customer.responsability_code)
        fexml.set_element('/fe:Invoice/fe:AccountingCustomerParty/cbc:AdditionalAccountID',
                          invoice.invoice_customer.organization_code)
        fexml.set_element('/fe:Invoice/fe:AccountingCustomerParty/fe:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_customer.name)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_customer.ident)
        fexml.set_element('/fe:Invoice/fe:AccountingCustomerParty/fe:Party/fe:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        fexml.set_element('/fe:Invoice/fe:AccountingCustomerParty/fe:Party/fe:PhysicalLocation/fe:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address)

        fexml.set_element('/fe:Invoice/fe:LegalMonetaryTotal/cbc:LineExtensionAmount',
                          invoice.invoice_legal_monetary_total.line_extension_amount,
                          currencyID='COP')
        fexml.set_element('/fe:Invoice/fe:LegalMonetaryTotal/cbc:TaxExclusiveAmount',
                          invoice.invoice_legal_monetary_total.tax_exclusive_amount,
                          currencyID='COP')
        fexml.set_element('/fe:Invoice/fe:LegalMonetaryTotal/cbc:TaxInclusiveAmount',
                          invoice.invoice_legal_monetary_total.tax_inclusive_amount,
                          currencyID='COP')
        fexml.set_element('/fe:Invoice/fe:LegalMonetaryTotal/cbc:ChargeTotalAmount',
                          invoice.invoice_legal_monetary_total.charge_total_amount,
                          currencyID='COP')
        fexml.set_element('/fe:Invoice/fe:LegalMonetaryTotal/cbc:PayableAmount',
                          invoice.invoice_legal_monetary_total.payable_amount,
                          currencyID='COP')

        fexml.set_element('/fe:Invoice/cbc:LineCountNumeric', len(invoice.invoice_lines))
        next_append = False
        for index, invoice_line in enumerate(invoice.invoice_lines):
            line = fexml.fragment('/fe:Invoice/fe:InvoiceLine', append=next_append)
            next_append = True

            line.set_element('/fe:InvoiceLine/cbc:ID', index + 1)
            line.set_element('/fe:InvoiceLine/cbc:InvoicedQuantity', invoice_line.quantity, unitCode = 'NAR')
            line.set_element('/fe:InvoiceLine/cbc:LineExtensionAmount', invoice_line.total_amount, currencyID="COP")
            line.set_element('/fe:InvoiceLine/fe:Price/cbc:PriceAmount', invoice_line.price_amount, currencyID="COP") 
            line.set_element('/fe:InvoiceLine/fe:Item/cbc:Description', invoice_line.description)


        return fexml
