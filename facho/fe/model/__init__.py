import facho.model as model
import facho.model.fields as fields
import facho.fe.form as form
from facho import fe

from datetime import date, datetime
from collections import defaultdict
from copy import copy
import hashlib

class Name(model.Model):
    __name__ = 'Name'

class Date(model.Model):
    __name__ = 'Date'

    def __default_set__(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, date):
            return value.isoformat()

    def __str__(self):
        return str(self._value)

class Time(model.Model):
    __name__ = 'Time'

    def __default_set__(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, date):
            return value.strftime('%H:%M:%S-05:00')

    def __str__(self):
        return str(self._value)

class InvoicePeriod(model.Model):
    __name__ = 'InvoicePeriod'

    start_date = fields.Many2One(Date, name='StartDate')

    end_date = fields.Many2One(Date, name='EndDate')

class ID(model.Model):
    __name__ = 'ID'

    def __default_get__(self, name, value):
        return self._value

    def __str__(self):
        return str(self._value)

class Party(model.Model):
    __name__ = 'Party'

    id = fields.Many2One(ID)

class AccountingCustomerParty(model.Model):
    __name__ = 'AccountingCustomerParty'

    party = fields.Many2One(Party)

class AccountingSupplierParty(model.Model):
    __name__ = 'AccountingSupplierParty'

    party = fields.Many2One(Party)

class Quantity(model.Model):
    __name__  = 'Quantity'

    code = fields.Attribute('unitCode', default='NAR')

    def __setup__(self):
        self.value = 0

    def __default_set__(self, value):
        self.value = value
        return value

    def __default_get__(self, name, value):
        return self.value

class Amount(model.Model):
    __name__ = 'Amount'

    currency = fields.Attribute('currencyID', default='COP')
    value = fields.Amount(name='amount', default=0.00, precision=2)

    def __default_set__(self, value):
        self.value = value
        return value

    def __default_get__(self, name, value):
        return self.value

    def __str__(self):
        return str(self.value)

class Price(model.Model):
    __name__ = 'Price'

    amount = fields.Many2One(Amount, name='PriceAmount')
    
    def __default_set__(self, value):
        self.amount = value
        return value

    def __default_get__(self, name, value):
        return self.amount

class Percent(model.Model):
    __name__ = 'Percent'

class TaxScheme(model.Model):
    __name__ = 'TaxScheme'

    id = fields.Many2One(ID)
    name= fields.Many2One(Name)

class TaxCategory(model.Model):
    __name__ = 'TaxCategory'

    percent = fields.Many2One(Percent)
    tax_scheme = fields.Many2One(TaxScheme)
    
class TaxSubTotal(model.Model):
    __name__ = 'TaxSubTotal'

    taxable_amount = fields.Many2One(Amount, name='TaxableAmount', default=0.00)
    tax_amount = fields.Many2One(Amount, name='TaxAmount', default=0.00)
    tax_percent = fields.Many2One(Percent)
    tax_category = fields.Many2One(TaxCategory)

    percent = fields.Virtual(setter='set_category', getter='get_category')
    scheme = fields.Virtual(setter='set_category', getter='get_category')

    def set_category(self, name, value):
        if name == 'percent':
            self.tax_category.percent = value
            # TODO(bit4bit) debe variar en conjunto?
            self.tax_percent = value
        elif name == 'scheme':
            self.tax_category.tax_scheme.id = value

        return value

    def get_category(self, name, value):
        if name == 'percent':
            return value
        elif name == 'scheme':
            return self.tax_category.tax_scheme

class TaxTotal(model.Model):
    __name__ = 'TaxTotal'

    tax_amount = fields.Many2One(Amount, name='TaxAmount', default=0.00)
    subtotals = fields.One2Many(TaxSubTotal)


class AllowanceCharge(model.Model):
    __name__ = 'AllowanceCharge'

    amount = fields.Many2One(Amount)
    is_discount = fields.Virtual(default=False)
    
    def isCharge(self):
        return self.is_discount == False

    def isDiscount(self):
        return self.is_discount == True

class Taxes:
    class Scheme:
        def __init__(self, scheme):
            self.scheme = scheme

    class Iva(Scheme):
        def __init__(self, percent):
            super().__init__('01')
            self.percent = percent

        def calculate(self, amount):
            return form.Amount(amount) * form.Amount(self.percent / 100)
    
class InvoiceLine(model.Model):
    __name__ = 'InvoiceLine'

    quantity = fields.Many2One(Quantity, name='InvoicedQuantity')
    taxtotal = fields.Many2One(TaxTotal)
    price = fields.Many2One(Price)
    amount = fields.Many2One(Amount, name='LineExtensionAmount')
    allowance_charge = fields.One2Many(AllowanceCharge)
    tax_amount = fields.Virtual(getter='get_tax_amount')
    
    def __setup__(self):
        self._taxs = defaultdict(list)
        self._subtotals = {}

    def add_tax(self, tax):
        if not isinstance(tax, Taxes.Scheme):
            raise ValueError('tax expected TaxIva')

        # inicialiamos subtotal para impuesto
        if not tax.scheme in self._subtotals:
            subtotal = self.taxtotal.subtotals.create()
            subtotal.scheme = tax.scheme
            
            self._subtotals[tax.scheme] = subtotal
        
        self._taxs[tax.scheme].append(tax)

    def get_tax_amount(self, name, value):
        total = form.Amount(0)
        for (scheme, subtotal) in self._subtotals.items():
            total += subtotal.tax_amount

        return total

    @fields.on_change(['price', 'quantity'])
    def update_amount(self, name, value):
        charge = form.AmountCollection(self.allowance_charge)\
            .filter(lambda charge: charge.isCharge())\
            .map(lambda charge: charge.amount)\
            .sum()

        discount = form.AmountCollection(self.allowance_charge)\
            .filter(lambda charge: charge.isDiscount())\
            .map(lambda charge: charge.amount)\
            .sum()

        total = form.Amount(self.quantity)  * form.Amount(self.price)
        self.amount = total + charge - discount
        
        for (scheme, subtotal) in self._subtotals.items():
            subtotal.tax_amount = 0

        for (scheme, taxes) in self._taxs.items():
            for tax in taxes:
                self._subtotals[scheme].tax_amount += tax.calculate(self.amount)

class LegalMonetaryTotal(model.Model):
    __name__ = 'LegalMonetaryTotal'

    line_extension_amount = fields.Many2One(Amount, name='LineExtensionAmount', default=0)

    tax_exclusive_amount = fields.Many2One(Amount, name='TaxExclusiveAmount', default=form.Amount(0))
    tax_inclusive_amount = fields.Many2One(Amount, name='TaxInclusiveAmount', default=form.Amount(0))
    charge_total_amount = fields.Many2One(Amount, name='ChargeTotalAmount', default=form.Amount(0))
    payable_amount = fields.Many2One(Amount, name='PayableAmount', default=form.Amount(0))

    @fields.on_change(['tax_inclusive_amount', 'charge_total'])
    def update_payable_amount(self, name, value):
        self.payable_amount = self.tax_inclusive_amount + self.charge_total_amount

class Invoice(model.Model):
    __name__ = 'Invoice'

    id = fields.Many2One(ID)
    issue = fields.Virtual(setter='set_issue')
    issue_date = fields.Many2One(Date, name='IssueDate')
    issue_time = fields.Many2One(Time, name='IssueTime')
    
    period = fields.Many2One(InvoicePeriod)

    supplier = fields.Many2One(AccountingSupplierParty)
    customer = fields.Many2One(AccountingCustomerParty)
    lines = fields.One2Many(InvoiceLine)
    legal_monetary_total = fields.Many2One(LegalMonetaryTotal)
    
    taxtotal_01 = fields.Many2One(TaxTotal)
    taxtotal_04 = fields.Many2One(TaxTotal)
    taxtotal_03 = fields.Many2One(TaxTotal)

    def __setup__(self):
        # Se requieren minimo estos impuestos para
        # validar el cufe
        self._subtotal_01 = self.taxtotal_01.subtotals.create()
        self._subtotal_01.scheme = '01'
        self._subtotal_01.percent = 19.0

        self._subtotal_04 = self.taxtotal_04.subtotals.create()
        self._subtotal_04.scheme = '04'
        
        self._subtotal_03 = self.taxtotal_03.subtotals.create()
        self._subtotal_03.scheme = '03'

    def cufe(self, token, environment):

        valor_bruto = self.legal_monetary_total.line_extension_amount
        valor_total_pagar = self.legal_monetary_total.payable_amount

        valor_impuesto_01 = form.Amount(0.0)
        valor_impuesto_04 = form.Amount(0.0)
        valor_impuesto_03 = form.Amount(0.0)

        for line in self.lines:
            for subtotal in line.taxtotal.subtotals:
                if subtotal.scheme.id == '01':
                    valor_impuesto_01 += subtotal.tax_amount
                elif subtotal.scheme.id == '04':
                    valor_impuesto_04 += subtotal.tax_amount
                elif subtotal.scheme.id == '03':
                    valor_impuesto_03 += subtotal.tax_amount

        pattern = [
            '%s' % str(self.id),
            '%s' % str(self.issue_date),
            '%s' % str(self.issue_time),
            valor_bruto.truncate_as_string(2),
            '01', valor_impuesto_01.truncate_as_string(2),
            '04', valor_impuesto_04.truncate_as_string(2),
            '03', valor_impuesto_03.truncate_as_string(2),
            valor_total_pagar.truncate_as_string(2),
            str(self.supplier.party.id),
            str(self.customer.party.id),
            str(token),
            str(environment)
        ]

        cufe = "".join(pattern)
        h = hashlib.sha384()
        h.update(cufe.encode('utf-8'))
        return h.hexdigest()

    @fields.on_change(['lines'])
    def update_legal_monetary_total(self, name, value):
        self.legal_monetary_total.line_extension_amount = 0
        self.legal_monetary_total.tax_inclusive_amount = 0

        for line in self.lines:
            self.legal_monetary_total.line_extension_amount += line.amount
            self.legal_monetary_total.tax_inclusive_amount += line.amount + line.tax_amount

    def set_issue(self, name, value):
        if not isinstance(value, datetime):
            raise ValueError('expected type datetime')
        self.issue_date = value.date()
        self.issue_time = value
