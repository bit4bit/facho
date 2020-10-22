# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import hashlib
from functools import reduce
import copy
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import decimal
from decimal import Decimal


from .data.dian import codelist

DECIMAL_PRECISION = 6

class AmountCurrencyError(TypeError):
    pass

@dataclass
class Currency:
    code: str

    def __eq__(self, other):
        return self.code == other.code

    def __str__(self):
        return self.code

class Collection:

    def __init__(self, array):
        self.array = array

    def filter(self, filterer):
        new_array = filter(filterer, self.array)
        return self.__class__(new_array)

    def map(self, mapper):
        new_array = map(mapper, self.array)
        return self.__class__(new_array)

    def sum(self):
        return sum(self.array)

class AmountCollection(Collection):

    def sum(self):
        total = Amount(0)
        for v in self.array:
            total += v
        return total

class Amount:
    def __init__(self, amount: int or float or Amount, currency: Currency = Currency('COP')):

        if isinstance(amount, Amount):
            self.amount = amount.amount
            self.currency = amount.currency
        else:
            self.amount = Decimal(amount, decimal.Context(prec=DECIMAL_PRECISION, rounding=decimal.ROUND_HALF_DOWN ))
            self.currency = currency

    def __round__(self, prec):
        return round(self.amount, prec)

    def __str__(self):
        return '%.06f' % self.amount

    def __eq__(self, other):
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return round(self.amount, DECIMAL_PRECISION) == round(other.amount, DECIMAL_PRECISION)

    def __add__(self, other):
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return Amount(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return Amount(self.amount - other.amount, self.currency)

    def __mul__(self, other):
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return Amount(self.amount * other.amount, self.currency)

    def is_same_currency(self, other):
        return self.currency == other.currency

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

    tax_amount: Amount = Amount(0.0)
    taxable_amount: Amount = Amount(0.0)

    def calculate(self, invline):
        self.tax_amount = invline.total_amount * Amount(self.percent / 100)
        self.taxable_amount = invline.total_amount


@dataclass
class TaxTotal:
    subtotals: list
    tax_amount: Amount = Amount(0.0)
    taxable_amount: Amount = Amount(0.0)

    def calculate(self, invline):
        for subtax in self.subtotals:
            subtax.calculate(invline)
            self.tax_amount += subtax.tax_amount
            self.taxable_amount += subtax.taxable_amount


@dataclass
class Price:
    amount: Amount
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
class PrePaidPayment:
    #DIAN 1.7.-2020: FBD03
    paid_amount: Amount = Amount(0.0)


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
        return Amount(self.quantity) * self.price.amount

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
    line_extension_amount: Amount = Amount(0.0)
    tax_exclusive_amount: Amount = Amount(0.0)
    tax_inclusive_amount: Amount = Amount(0.0)
    charge_total_amount: Amount = Amount(0.0)
    allowance_total_amount: Amount = Amount(0.0)
    payable_amount: Amount = Amount(0.0)
    prepaid_amount: Amount = Amount(0.0)

@dataclass
class AllowanceCharge:
    #DIAN 1.7.-2020: FAQ03
    charge_indicator: bool = True
    amount: Amount = Amount(0.0)

    def isCharge(self):
        return self.charge_indicator == True

    def isDiscount(self):
        return self.charge_indicator == False

    def asCharge(self):
        self.charge_indicator = True

    def asDiscount(self):
        self.charge_indicator = False



class Invoice:
    def __init__(self):
        self.invoice_period_start = None
        self.invoice_period_end = None
        self.invoice_issue = None
        self.invoice_ident = None
        self.invoice_operation_type = None
        self.invoice_legal_monetary_total = LegalMonetaryTotal()
        self.invoice_customer = None
        self.invoice_supplier = None
        self.invoice_payment_mean = None
        self.invoice_payments = []
        self.invoice_lines = []
        self.invoice_allowance_charge = []
        self.invoice_prepaid_payment = []

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

    def add_allownace_charge(self, charge: AllowanceCharge):
        self.invoice_allowance_charge.append(charge)

    def add_invoice_line(self, line: InvoiceLine):
        self.invoice_lines.append(line)

    def add_prepaid_payment(self, paid: PrePaidPayment):
        self.invoice_prepaid_payment.append(paid)

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

        #DIAN 1.7.-2020: FAU08
        self.invoice_legal_monetary_total.allowance_total_amount = AmountCollection(self.invoice_allowance_charge)\
            .filter(lambda charge: charge.isDiscount())\
            .map(lambda charge: charge.amount)\
            .sum()

        #DIAN 1.7.-2020: FAU10
        self.invoice_legal_monetary_total.charge_total_amount = AmountCollection(self.invoice_allowance_charge)\
            .filter(lambda charge: charge.isCharge())\
            .map(lambda charge: charge.amount)\
            .sum()

        #DIAN 1.7.-2020: FAU12
        self.invoice_legal_monetary_total.prepaid_amount = AmountCollection(self.invoice_prepaid_payment)\
            .map(lambda paid: paid.paid_amount)\
            .sum()

        #DIAN 1.7.-2020: FAU14
        self.invoice_legal_monetary_total.payable_amount = \
            self.invoice_legal_monetary_total.tax_inclusive_amount \
            + self.invoice_legal_monetary_total.allowance_total_amount \
            + self.invoice_legal_monetary_total.charge_total_amount \
            - self.invoice_legal_monetary_total.prepaid_amount


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
