# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import hashlib
from functools import reduce
import copy
import dataclasses
from dataclasses import dataclass
from datetime import datetime, date
from collections import defaultdict
import decimal
from decimal import Decimal
import typing

from ..data.dian import codelist

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
    def __init__(self, amount: int or float or str or Amount, currency: Currency = Currency('COP'), precision = DECIMAL_PRECISION):
        self.precision = precision
        #DIAN 1.7.-2020: 1.2.3.1
        if isinstance(amount, Amount):
            if amount < Amount(0.0):
                raise ValueError('amount must be positive >= 0')

            self.amount = amount.amount
            self.currency = amount.currency
        else:
            if float(amount) < 0:
                raise ValueError('amount must be positive >= 0')

            self.amount = Decimal(amount, decimal.Context(prec=self.precision,
                                                          #DIAN 1.7.-2020: 1.2.1.1
                                                          rounding=decimal.ROUND_HALF_EVEN ))
            self.currency = currency

    def fromNumber(self, val):
        return Amount(val, currency=self.currency)
    
    def round(self, prec):
        return Amount(round(self.amount, prec), currency=self.currency)

    def __round__(self, prec):
        return round(self.amount, prec)

    def __str__(self):
        return str(self.float())

    def __lt__(self, other):
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return round(self.amount, self.precision) < round(other, 2)

    def __eq__(self, other):
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return round(self.amount, self.precision) == round(other.amount, self.precision)

    def _cast(self, val):
        if type(val) in [int, float]:
            return self.fromNumber(val)
        if isinstance(val, Amount):
            return val
        if isinstance(val, Decimal):
            return self.fromNumber(float(val))

        raise TypeError("cant cast %s to amount" % (type(val)))
    
    def __add__(self, rother):
        other = self._cast(rother)
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return Amount(self.amount + other.amount, self.currency)

    def __sub__(self, rother):
        other = self._cast(rother)
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return Amount(self.amount - other.amount, self.currency)

    def __mul__(self, rother):
        other = self._cast(rother)
        if not self.is_same_currency(other):
            raise AmountCurrencyError()
        return Amount(self.amount * other.amount, self.currency)

    def is_same_currency(self, other):
        return self.currency == other.currency

    def truncate_as_string(self, prec):
        parts = str(self.float()).split('.', 1)
        return '%s.%s' % (parts[0], parts[1][0:prec].ljust(prec,'0'))

    def float(self):
        return float(round(self.amount, DECIMAL_PRECISION))
    

class Quantity:
    
    def __init__(self, val, code):
        if type(val) not in [float, int]:
            raise ValueError('val expected int or float')
        if code not in codelist.UnidadesMedida:
            raise ValueError("code [%s] not found" % (code))

        self.value = Amount(val)
        self.code = code

    def __mul__(self, other):
        return self.value * other

    def __lt__(self, other):
        return self.value < other

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

@dataclass
class Item:
    scheme_name: str
    scheme_agency_id: str
    scheme_id: str
    description: str
    id: str


class StandardItem(Item):
    def __init__(self, id_: str, description: str = ''):
        super().__init__(id=id_,
                         description=description,
                         scheme_name='',
                         scheme_id='999',
                         scheme_agency_id='')


class UNSPSCItem(Item):
    def __init__(self, id_: str, description: str = ''):
        super().__init__(id=id_,
                         description=description,
                         scheme_name='UNSPSC',
                         scheme_id='001',
                         scheme_agency_id='10')        

        
@dataclass
class Country:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.Paises:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.Paises[self.code]['name']

@dataclass
class CountrySubentity:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.Departamento:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.Departamento[self.code]['name']

@dataclass
class City:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.Municipio:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.Municipio[self.code]['name']

@dataclass
class Address:
    name: str
    street: str = ''
    city: City = City('05001')
    country: Country = Country('CO')
    countrysubentity: CountrySubentity = CountrySubentity('05')

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

    def __post_init__(self):
        if self.type_fiscal not in codelist.TipoIdFiscal:
            raise ValueError("type_fiscal [%s] not found" % (self.type_fiscal))

@dataclass
class Responsability:
    codes: list

    def __str__(self):
        return ';'.join(self.codes)

    def __eq__(self, other):
        return str(self) == str(other)

    def __iter__(self):
        return iter(self.codes)

    def __post_init__(self):
        for code in self.codes:
            if code not in codelist.TipoResponsabilidad:
                raise ValueError("code %s not found" % (code))


@dataclass
class TaxScheme:
    code: str
    name: str = ''


    def __post_init__(self):
        if self.code not in codelist.TipoImpuesto:
            raise ValueError("code not found")
        self.name = codelist.TipoImpuesto[self.code]['name']

@dataclass
class Party:
    name: str
    ident: str
    responsability_code: typing.List[Responsability]
    responsability_regime_code: str
    organization_code: str
    tax_scheme: TaxScheme = TaxScheme('01')

    phone: str = ''
    address: Address = Address('')
    email: str = ''
    legal_name: str = ''
    legal_company_ident: str = ''
    legal_address: str = ''

    def __post_init__(self):
        if self.organization_code not in codelist.TipoOrganizacion:
            raise ValueError("organization_code not found")


@dataclass
class TaxScheme:
    code: str = '01'

    @property
    def name(self):
        return codelist.TipoImpuesto[self.code]['name']

    def __post_init__(self):
        if self.code not in codelist.TipoImpuesto:
            raise ValueError("code [%s] not found" % (self.code))


@dataclass
class TaxSubTotal:
    percent: float
    scheme: typing.Optional[TaxScheme] = None
    tax_amount: Amount = Amount(0.0)

    def calculate(self, invline):
        if self.percent is not None:
            self.tax_amount = invline.total_amount * Amount(self.percent / 100)


@dataclass
class TaxTotal:
    subtotals: list
    tax_amount: Amount = Amount(0.0)
    taxable_amount: Amount = Amount(0.0)

    def calculate(self, invline):
        self.taxable_amount = invline.total_amount

        for subtax in self.subtotals:
            subtax.calculate(invline)
            self.tax_amount += subtax.tax_amount


class TaxTotalOmit(TaxTotal):
    def __init__(self):
        super().__init__([])

    def calculate(self, invline):
        pass

@dataclass
class Price:
    amount: Amount
    type_code: str
    type: str
    quantity: int = 1

    def __post_init__(self):
        if self.type_code not in codelist.CodigoPrecioReferencia:
            raise ValueError("type_code [%s] not found" % (self.type_code))
        if not isinstance(self.quantity, int):
            raise ValueError("quantity must be int")

        self.amount *= self.quantity

@dataclass
class PaymentMean:
    DEBIT = '01'
    CREDIT = '02'

    def __init__(self, id: str, code: str, due_at: datetime, payment_id: str):
        if code not in codelist.MediosPago:
            raise ValueError("code not found")

        self.id = id
        self.code = code
        self.due_at = due_at
        self.payment_id = payment_id


@dataclass
class PrePaidPayment:
    #DIAN 1.7.-2020: FBD03
    paid_amount: Amount = Amount(0.0)


@dataclass
class BillingReference:
    ident: str
    uuid: str
    date: date

class CreditNoteDocumentReference(BillingReference):
    """
    ident: Prefijo + Numero de la factura relacionada
    uuid: CUFE de la factura electronica
    date: fecha de emision de la factura relacionada
    """


class DebitNoteDocumentReference(BillingReference):
    """
    ident: Prefijo + Numero de la factura relacionada
    uuid: CUFE de la factura electronica
    date: fecha de emision de la factura relacionada
    """

class InvoiceDocumentReference(BillingReference):
    """
    ident: Prefijo + Numero de la nota credito relacionada
    uuid: CUDE de la nota credito relacionada
    date: fecha de emision de la nota credito relacionada
    """

@dataclass
class AllowanceChargeReason:
    code: str
    reason: str

    def __post_init__(self):
        if self.code not in codelist.CodigoDescuento:
            raise ValueError("code [%s] not found" % (self.code))


@dataclass
class AllowanceCharge:
    #DIAN 1.7.-2020: FAQ03
    charge_indicator: bool = True
    amount: Amount = Amount(0.0)
    reason: AllowanceChargeReason = None

    #Valor Base para calcular el descuento o el cargo
    base_amount: typing.Optional[Amount] = Amount(0.0)
    
    # Porcentaje: Porcentaje que aplicar.
    multiplier_factor_numeric: Amount = Amount(1.0)
    
    def isCharge(self):
        return self.charge_indicator == True

    def isDiscount(self):
        return self.charge_indicator == False

    def asCharge(self):
        self.charge_indicator = True

    def asDiscount(self):
        self.charge_indicator = False

    def hasReason(self):
        return self.reason is not None

    def set_base_amount(self, amount):
        self.base_amount = amount

class AllowanceChargeAsDiscount(AllowanceCharge):
    def __init__(self, amount: Amount = Amount(0.0)):
        self.charge_indicator = False
        self.amount = amount

@dataclass
class InvoiceLine:
    # RESOLUCION 0004: pagina 155
    quantity: Quantity
    description: str
    item: Item
    price: Price
    # TODO mover a Invoice
    # ya que al reportar los totales es sobre
    # la factura y el percent es unico por type_code
    # de subtotal
    tax: typing.Optional[TaxTotal]

    allowance_charge: typing.List[AllowanceCharge] = dataclasses.field(default_factory=list)

    def add_allowance_charge(self, charge):
        if not isinstance(charge, AllowanceCharge):
            raise TypeError('charge invalid type expected AllowanceCharge')
        charge.set_base_amount(self.total_amount_without_charge)
        self.allowance_charge.add(charge)

    @property
    def total_amount_without_charge(self):
        return (self.quantity * self.price.amount)
    
    @property
    def total_amount(self):
        charge = AmountCollection(self.allowance_charge)\
            .filter(lambda charge: charge.isCharge())\
            .map(lambda charge: charge.amount)\
            .sum()

        discount = AmountCollection(self.allowance_charge)\
            .filter(lambda charge: charge.isDiscount())\
            .map(lambda charge: charge.amount)\
            .sum()

        return self.total_amount_without_charge + charge - discount

    @property
    def total_tax_inclusive_amount(self):
        # FAU06
        return self.total_amount + self.tax.tax_amount

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

    def __post_init__(self):
        if not isinstance(self.quantity, Quantity):
            raise ValueError("quantity must be Amount")

        if self.tax is None:
            self.tax = TaxTotalOmit()

@dataclass
class LegalMonetaryTotal:
    line_extension_amount: Amount = Amount(0.0)
    tax_exclusive_amount: Amount = Amount(0.0)
    tax_inclusive_amount: Amount = Amount(0.0)
    charge_total_amount: Amount = Amount(0.0)
    allowance_total_amount: Amount = Amount(0.0)
    payable_amount: Amount = Amount(0.0)
    prepaid_amount: Amount = Amount(0.0)

    def calculate(self):
        #DIAN 1.7.-2020: FAU14
        self.payable_amount = \
            self.tax_inclusive_amount \
            + self.allowance_total_amount \
            + self.charge_total_amount \
            - self.prepaid_amount



class NationalSalesInvoiceDocumentType(str):
    def __str__(self):
        # 6.1.3
        return '01'

class CreditNoteDocumentType(str):
    def __str__(self):
        # 6.1.3
        return '91'

class DebitNoteDocumentType(str):
    def __str__(self):
        # 6.1.3
        return '92'

class Invoice:
    def __init__(self, type_code: str):
        if str(type_code) not in codelist.TipoDocumento:
            raise ValueError("type_code [%s] not found")

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
        self.invoice_billing_reference = None
        self.invoice_type_code = str(type_code)
        self.invoice_ident_prefix = None

    def set_period(self, startdate, enddate):
        self.invoice_period_start = startdate
        self.invoice_period_end = enddate

    def set_issue(self, dtime: datetime):
        if dtime.tzname() not in ['UTC-05:00', '-05', None]:
            raise ValueError("dtime must be UTC-05:00")

        self.invoice_issue = dtime

    def _set_ident_prefix_automatic(self):
        if not self.invoice_ident_prefix:
            prefix = ''
            for idx, val in enumerate(self.invoice_ident):
                if val.isalpha():
                    prefix += val
                else:
                    break

            if len(prefix) <= 4:
                self.invoice_ident_prefix = prefix
            else:
                raise ValueError('ident prefix failed to get, expected 0  to 4 chars')

    def set_ident(self, ident: str):
        """
        identificador de factura; prefijo + consecutivo
        """
        self.invoice_ident = ident
        self._set_ident_prefix_automatic()

    def _check_ident_prefix(self, prefix):
        if len(prefix) != 4:
            raise ValueError('prefix must be 4 length')

    def set_ident_prefix(self, prefix: str):
        """
        prefijo de facturacion: ejemplo SETP
        """
        self._check_ident_prefix(prefix)
        self.invoice_ident_prefix = prefix

    def set_supplier(self, party: Party):
        self.invoice_supplier = party

    def set_customer(self, party: Party):
        self.invoice_customer = party

    def set_payment_mean(self, payment_mean: PaymentMean):
        self.invoice_payment_mean = payment_mean

    def _get_codelist_tipo_operacion(self):
        return codelist.TipoOperacionF
    
    def set_operation_type(self, operation):
        if operation not in self._get_codelist_tipo_operacion():
            raise ValueError("operation not found")

        self.invoice_operation_type = operation

    def add_allowance_charge(self, charge: AllowanceCharge):
        self.invoice_allowance_charge.append(charge)

    def add_invoice_line(self, line: InvoiceLine):
        self.invoice_lines.append(line)

    def add_prepaid_payment(self, paid: PrePaidPayment):
        self.invoice_prepaid_payment.append(paid)

    def set_billing_reference(self, billing_reference: BillingReference):
        self.invoice_billing_reference = billing_reference

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
        self.invoice_legal_monetary_total.calculate()

    def _refresh_charges_base_amount(self):
        if self.invoice_allowance_charge:
            for invline in self.invoice_lines:
                if invline.allowance_charge:
                    # TODO actualmente solo uno de los cargos es permitido
                    raise ValueError('allowance charge in invoice exclude invoice line')
            
        # cargos a nivel de factura
        for charge in self.invoice_allowance_charge:
            charge.set_base_amount(self.invoice_legal_monetary_total.line_extension_amount)
        
    def calculate(self):
        for invline in self.invoice_lines:
            invline.calculate()
        self._calculate_legal_monetary_total()
        self._refresh_charges_base_amount()

class NationalSalesInvoice(Invoice):
    def __init__(self):
        super().__init__(NationalSalesInvoiceDocumentType())


class CreditNote(Invoice):
    def __init__(self, invoice_document_reference: BillingReference):
        super().__init__(CreditNoteDocumentType())

        if not isinstance(invoice_document_reference, BillingReference):
            raise TypeError('invoice_document_reference invalid type')
        self.invoice_billing_reference = invoice_document_reference

    def _get_codelist_tipo_operacion(self):
        return codelist.TipoOperacionNC
    
    def _check_ident_prefix(self, prefix):
        if len(prefix) != 6:
            raise ValueError('prefix must be 6 length')

    def _set_ident_prefix_automatic(self):
        if not self.invoice_ident_prefix:
            self.invoice_ident_prefix = self.invoice_ident[0:6]


class DebitNote(Invoice):
    def __init__(self, invoice_document_reference: BillingReference):
        super().__init__(DebitNoteDocumentType())

        if not isinstance(invoice_document_reference, BillingReference):
            raise TypeError('invoice_document_reference invalid type')
        self.invoice_billing_reference = invoice_document_reference

    def _get_codelist_tipo_operacion(self):
        return codelist.TipoOperacionND

    def _check_ident_prefix(self, prefix):
        if len(prefix) != 6:
            raise ValueError('prefix must be 6 length')

    def _set_ident_prefix_automatic(self):
        if not self.invoice_ident_prefix:
            self.invoice_ident_prefix = self.invoice_ident[0:6]

