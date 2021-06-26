import facho.model as model
import facho.model.fields as fields
from datetime import date, datetime

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

class InvoicedQuantity(model.Model):
    __name__  = 'InvoiceQuantity'

    code = fields.Attribute('unitCode', default='NAR')


class PriceAmount(model.Model):
    __name__ = 'PriceAmount'

    currency = fields.Attribute('currencyID', default='COP')
    
class Price(model.Model):
    __name__ = 'Price'

    amount = fields.Many2One(PriceAmount)

    def __default_set__(self, value):
        self.amount = value

class InvoiceLine(model.Model):
    __name__ = 'InvoiceLine'

    quantity = fields.Many2One(InvoicedQuantity)
    price = fields.Many2One(Price)
    
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

    def set_issue(self, name, value):
        if not isinstance(value, datetime):
            raise ValueError('expected type datetime')
        self.issue_date = value
        self.issue_time = value
