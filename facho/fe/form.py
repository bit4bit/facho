# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import hashlib
from functools import reduce
import copy
from dataclasses import dataclass
from datetime import datetime

from .data import dian
from . import fe

class DataError(Exception):

    def __init__(self, errors):
        self._errors = errors

        
class DataValidator:

    # valida y  retorna errores [(key, error)..]
    def validate(self) -> []:
        raise NotImplementedError()

    def try_validate(self):
        errors = self.validate()
        if errors:
            raise DataError(errors)
    

@dataclass
class Party(DataValidator):
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

    def validate(self):
        errors = []
        try:
            dian.TipoResponsabilidad[self.responsability_code]
        except KeyError:
            errors.append(('responsability_code', 'not found'))

        try:
            dian.TipoOrganizacion[self.organization_code]
        except KeyError:
            errors.append(('organization_code', 'not found'))

        
        return errors


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
        return self.tax.taxable_amount

    @property
    def total_tax_exclusive_amount(self):
        return self.tax.tax_amount

    def calculate(self):
        self.tax.calculate(self)


@dataclass
class LegalMonetaryTotal:
    line_extension_amount: float = 0.0
    tax_exclusive_amount: float = 0.0
    tax_inclusive_amount: float = 0.0
    charge_total_amount: float = 0.0
    payable_amount: float = 0.0


class Invoice(DataValidator):
    def __init__(self):
        self.invoice_period_start = None
        self.invoice_period_end = None
        self.invoice_issue = None
        self.invoice_ident = None
        self.invoice_cufe = None
        self.invoice_legal_monetary_total = LegalMonetaryTotal(0, 0, 0, 0, 0)
        self.invoice_customer = None
        self.invoice_supplier = None
        self.invoice_lines = []
        self.errors = []
        
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

    def validate(self):
        errors_customer = [('customer.%s' % (field), err) for field, err in self.invoice_customer.validate()]
        errors_supplier = [('supplier.%s' % (field), err) for field, err in self.invoice_customer.validate()]
        self.errors = errors_customer + errors_supplier

    def valid(self):
        self.validate()
        return not self.errors

    def _calculate_legal_monetary_total(self):
        for invline in self.invoice_lines:
            self.invoice_legal_monetary_total.line_extension_amount += invline.total_amount
            self.invoice_legal_monetary_total.tax_exclusive_amount += invline.total_amount
            self.invoice_legal_monetary_total.charge_total_amount += invline.total_amount

        self.invoice_legal_monetary_total.payable_amount = self.invoice_legal_monetary_total.tax_exclusive_amount \
            + self.invoice_legal_monetary_total.line_extension_amount \
            + self.invoice_legal_monetary_total.tax_inclusive_amount

    def calculate(self):
        self._calculate_legal_monetary_total()
        for invline in self.invoice_lines:
            invline.calculate()

class DIANInvoiceXML(fe.FeXML):

    def __init__(self, invoice, TipoAmbiente = 'Pruebas'):
        super().__init__('Invoice', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')
        self.attach_invoice(invoice, TipoAmbiente)
        
    def attach_invoice(self, invoice, TipoAmbiente):
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""
        fexml = self

        invoice.try_validate()
        invoice.calculate()

        cufe = self._generate_cufe(invoice, TipoAmbiente)

        fexml.set_element('/fe:Invoice/cbc:ID', invoice.invoice_ident)
        fexml.set_element('/fe:Invoice/cbc:UUID[schemaName="CUFE-SHA384"]', cufe)
        fexml.set_element('/fe:Invoice/cbc:IssueDate', invoice.invoice_issue.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:Invoice/cbc:IssueTime', invoice.invoice_issue.strftime('%H:%M:%S'))
        fexml.set_element('/fe:Invoice/cac:InvoicePeriod/cbc:StartDate', invoice.invoice_period_start.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:Invoice/cac:InvoicePeriod/cbc:EndDate', invoice.invoice_period_end.strftime('%Y-%m-%d'))

        fexml.set_element('/fe:Invoice/cbc:LineCountNumeric', len(invoice.invoice_lines))

        fexml.set_element('/fe:Invoice/fe:AccountingSupplierParty/fe:Party/cac:PartyIdentification/cbc:ID',
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
                          
        for index, invoice_line in enumerate(invoice.invoice_lines):
            line = fexml.fragment('/fe:Invoice/fe:InvoiceLine', append=True)

            line.set_element('/fe:InvoiceLine/cbc:ID', index)
            line.set_element('/fe:InvoiceLine/cbc:InvoicedQuantity', invoice_line.quantity, unitCode = 'NAR')
            line.set_element('/fe:InvoiceLine/cbc:LineExtensionAmount', invoice_line.total_amount, currencyID="COP")
            line.set_element('/fe:InvoiceLine/fe:Price/cbc:PriceAmount', invoice_line.price_amount, currencyID="COP") 
            line.set_element('/fe:InvoiceLine/fe:Item/cbc:Description', invoice_line.description)

        return fexml


    def _generate_cufe(self, invoice, TipoAmbiente = 'Pruebas'):
        NumFac = invoice.invoice_ident
        FecFac = invoice.invoice_issue.strftime('%Y-%m-%d')
        HoraFac = invoice.invoice_issue.strftime('%H:%H:%S')
        ValorBruto = invoice.invoice_legal_monetary_total.line_extension_amount
        ValorTotalPagar = invoice.invoice_legal_monetary_total.payable_amount
        ValorImpuestoPara = {}
        ValorImpuesto1 = 0.0
        CodImpuesto1 = 1
        ValorImpuesto2 = 0.0
        CodImpuesto2 = 4
        ValorImpuesto3 = 0.0
        CodImpuesto3 = 3
        for invoice_line in invoice.invoice_lines:
            for subtotal in invoice_line.tax.subtotals:
                # TODO cual es la naturaleza de tax_scheme_ident?
                codigo_impuesto = int(subtotal.tax_scheme_ident)
                ValorImpuestoPara.setdefault(codigo_impuesto, 0.0)
                ValorImpuestoPara[codigo_impuesto] += subtotal.tax_amount

        NitOFE = invoice.invoice_supplier.ident
        NumAdq = invoice.invoice_customer.ident
        TipoAmb = int(dian.TipoAmbiente[TipoAmbiente]['code'])

        formatVars = {
            '%s': NumFac,
            '%s': FecFac,
            '%.02f': HoraFac,
            '%.02f': ValorBruto,
            '%.02f': ValorTotalPagar,
            '%.02f': ValorImpuestoPara.get(CodImpuesto1, 0.0),
            '%02d': CodImpuesto1,
            '%.02f': ValorImpuestoPara.get(CodImpuesto2, 0.0),
            '%02d': CodImpuesto2,
            '%.02f': ValorImpuestoPara.get(CodImpuesto3, 0.0),
            '%02d': CodImpuesto3,
            '%s': NitOFE,
            '%s': NumAdq,
            '%d': TipoAmb,
        }
        cufe = "".join(formatVars.keys()) % tuple(formatVars.values())

        # crear hash...
        h = hashlib.sha384()
        h.update(cufe.encode('utf-8'))
        return h.hexdigest()

