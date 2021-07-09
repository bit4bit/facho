import facho.model as model
import facho.model.fields as fields
import facho.fe.form as form
from datetime import date, datetime
from copy import copy

class Name(model.Model):
    __name__ = 'Name'

class Date(model.Model):
    __name__ = 'Date'

    def __default_set__(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, date):
            return value.isoformat()

class Time(model.Model):
    __name__ = 'Time'

    def __default_set__(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, date):
            return value.strftime('%H:%M%S-05:00')

class InvoicePeriod(model.Model):
    __name__ = 'InvoicePeriod'

    start_date = fields.Many2One(Date, name='StartDate')

    end_date = fields.Many2One(Date, name='EndDate')

class ID(model.Model):
    __name__ = 'ID'

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
    value = fields.Virtual(default=0, update_internal=True)

    def __default_set__(self, value):
        self.value = value
        return value

    def __mul__(self, other):
        return form.Amount(self.value) * other.value


class Amount(model.Model):
    __name__ = 'Amount'

    currency = fields.Attribute('currencyID', default='COP')
    value = fields.Virtual(default=form.Amount(0), update_internal=True)

    def __default_set__(self, value):
        self.value = value
        return value

class Price(model.Model):
    __name__ = 'Price'

    amount = fields.Many2One(Amount, name='PriceAmount')
    value = fields.Virtual(default=form.Amount(0))
    
    def __default_set__(self, value):
        self.amount = value
        self.value = value
        return value

    def __mul__(self, other):
        return self.value * other.value


class Percent(model.Model):
    __name__ = 'Percent'

class TaxScheme(model.Model):
    __name__ = 'TaxScheme'

    id = fields.Many2One(ID)
    name= fields.Many2One(Name)

class TaxCategory(model.Model):
    __name__ = 'TaxCategory'

    percent = fields.Many2One(Percent, default='19.0')
    tax_scheme = fields.Many2One(TaxScheme)
    
class TaxSubTotal(model.Model):
    __name__ = 'TaxSubTotal'

    taxable_amount = fields.Many2One(Amount, name='TaxableAmount')
    tax_amount = fields.Many2One(Amount, name='TaxAmount')
    tax_category = fields.Many2One(TaxCategory)

    percent = fields.Virtual(setter='set_category')
    scheme = fields.Virtual(setter='set_category')
    def set_category(self, name, value):
        if name == 'percent':
            self.tax_category.percent = value
            # TODO(bit4bit) hacer variable
            self.tax_category.tax_scheme.id = '01'
            self.tax_category.tax_scheme.name = 'IVA'
        elif name == 'scheme':
            self.tax_category.tax_scheme.id = value
            
    
class TaxTotal(model.Model):
    __name__ = 'TaxTotal'

    tax_amount = fields.Many2One(Amount, name='TaxAmount')
    subtotals = fields.One2Many(TaxSubTotal)


class AllowanceCharge(model.Model):
    __name__ = 'AllowanceCharge'

    amount = fields.Many2One(Amount)
    is_discount = fields.Virtual(default=False)
    
    def isCharge(self):
        return self.is_discount == False

    def isDiscount(self):
        return self.is_discount == True

class InvoiceLine(model.Model):
    __name__ = 'InvoiceLine'

    quantity = fields.Many2One(Quantity, name='InvoicedQuantity')
    taxtotal = fields.Many2One(TaxTotal)
    price = fields.Many2One(Price)
    amount = fields.Many2One(Amount, name='LineExtensionAmount')
    allowance_charge = fields.One2Many(AllowanceCharge)

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

        total = self.quantity  * self.price
        self.amount = total + charge - discount

class LegalMonetaryTotal(model.Model):
    __name__ = 'LegalMonetaryTotal'

    line_extension_amount = fields.Many2One(Amount, name='LineExtensionAmount', default=form.Amount(0))
    tax_exclusive_amount = fields.Many2One(Amount, name='TaxExclusiveAmount')
    tax_inclusive_amount = fields.Many2One(Amount, name='TaxInclusiveAmount')
    charge_total_amount = fields.Many2One(Amount, name='ChargeTotalAmount')
    payable_amount = fields.Many2One(Amount, name='PayableAmount')
    
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

    cufe = fields.Virtual()

    @fields.on_change(['lines'])
    def update_legal_monetary_total(self, name, value):
        for line in self.lines:
            self.legal_monetary_total.line_extension_amount.value += line.amount.value
            
    def set_issue(self, name, value):
        if not isinstance(value, datetime):
            raise ValueError('expected type datetime')
        self.issue_date = value
        self.issue_time = value
