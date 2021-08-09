import facho.model as model
import facho.model.fields as fields
import facho.fe.form as form
from facho import fe
from .common import *
from . import dian

from datetime import date, datetime
from collections import defaultdict
from copy import copy
import hashlib



class PhysicalLocation(model.Model):
    __name__ = 'PhysicalLocation'

    address = fields.Many2One(Address, namespace='cac')
    
class PartyTaxScheme(model.Model):
    __name__ = 'PartyTaxScheme'

    company_id = fields.Many2One(ID, name='CompanyID', namespace='cbc')
    tax_level_code = fields.Many2One(ID, name='TaxLevelCode', namespace='cbc', default='ZZ')
    
class Party(model.Model):
    __name__ = 'Party'

    id = fields.Virtual(setter='_on_set_id')

    tax_scheme = fields.Many2One(PartyTaxScheme, namespace='cac')
    location = fields.Many2One(PhysicalLocation, namespace='cac')
    
    def _on_set_id(self, name, value):
        self.tax_scheme.company_id = value
        return value

class AccountingCustomerParty(model.Model):
    __name__ = 'AccountingCustomerParty'

    party = fields.Many2One(Party, namespace='cac')

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

    amount = fields.Many2One(Amount, name='PriceAmount', namespace='cbc')
    
    def __default_set__(self, value):
        self.amount = value
        return value

    def __default_get__(self, name, value):
        return self.amount

class Percent(model.Model):
    __name__ = 'Percent'

class TaxScheme(model.Model):
    __name__ = 'TaxScheme'

    id = fields.Many2One(ID, namespace='cbc')
    name= fields.Many2One(Name, namespace='cbc')

class TaxCategory(model.Model):
    __name__ = 'TaxCategory'

    percent = fields.Many2One(Percent, namespace='cbc')
    tax_scheme = fields.Many2One(TaxScheme, namespace='cac')
    
class TaxSubTotal(model.Model):
    __name__ = 'TaxSubTotal'

    taxable_amount = fields.Many2One(Amount, name='TaxableAmount', namespace='cbc', default=0.00)
    tax_amount = fields.Many2One(Amount, name='TaxAmount', namespace='cbc', default=0.00)
    tax_percent = fields.Many2One(Percent, namespace='cbc')
    tax_category = fields.Many2One(TaxCategory, namespace='cac')

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

    tax_amount = fields.Many2One(Amount, name='TaxAmount', namespace='cbc', default=0.00)
    subtotals = fields.One2Many(TaxSubTotal, namespace='cac')


class AllowanceCharge(model.Model):
    __name__ = 'AllowanceCharge'

    amount = fields.Many2One(Amount, namespace='cbc')
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

    id = fields.Many2One(ID, namespace='cbc')
    quantity = fields.Many2One(Quantity, name='InvoicedQuantity', namespace='cbc')
    taxtotal = fields.Many2One(TaxTotal, namespace='cac')
    price = fields.Many2One(Price, namespace='cac')
    amount = fields.Many2One(Amount, name='LineExtensionAmount', namespace='cbc')
    allowance_charge = fields.One2Many(AllowanceCharge, 'cac')
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

    line_extension_amount = fields.Many2One(Amount, name='LineExtensionAmount', namespace='cbc', default=0)

    tax_exclusive_amount = fields.Many2One(Amount, name='TaxExclusiveAmount', namespace='cbc', default=form.Amount(0))
    tax_inclusive_amount = fields.Many2One(Amount, name='TaxInclusiveAmount', namespace='cbc', default=form.Amount(0))
    charge_total_amount = fields.Many2One(Amount, name='ChargeTotalAmount', namespace='cbc', default=form.Amount(0))
    payable_amount = fields.Many2One(Amount, name='PayableAmount', namespace='cbc', default=form.Amount(0))

    @fields.on_change(['tax_inclusive_amount', 'charge_total'])
    def update_payable_amount(self, name, value):
        self.payable_amount = self.tax_inclusive_amount + self.charge_total_amount


class DIANExtensionContent(model.Model):
    __name__ = 'ExtensionContent'
    
    dian = fields.Many2One(dian.DianExtensions, name='DianExtensions', namespace='sts')

class DIANExtension(model.Model):
    __name__ = 'UBLExtension'

    content = fields.Many2One(DIANExtensionContent, namespace='ext')

    def __default_get__(self, name, value):
        return self.content.dian

class UBLExtension(model.Model):
    __name__ = 'UBLExtension'

    content = fields.Many2One(Element, name='ExtensionContent', namespace='ext', default='')
    
class UBLExtensions(model.Model):
    __name__ = 'UBLExtensions'

    dian = fields.Many2One(DIANExtension, namespace='ext', create=True)
    extension = fields.Many2One(UBLExtension, namespace='ext', create=True)

class Invoice(model.Model):
    __name__ = 'Invoice'
    __namespace__ = fe.NAMESPACES

    _ubl_extensions = fields.Many2One(UBLExtensions, namespace='ext')
    # nos interesa el acceso solo los atributos de la DIAN
    dian = fields.Virtual(getter='get_dian_extension')
    
    profile_id = fields.Many2One(Element, name='ProfileID', namespace='cbc', default='DIAN 2.1')
    profile_execute_id = fields.Many2One(Element, name='ProfileExecuteID', namespace='cbc', default='2')
    
    id = fields.Many2One(ID, namespace='cbc')
    issue = fields.Virtual(setter='set_issue')
    issue_date = fields.Many2One(Date, name='IssueDate', namespace='cbc')
    issue_time = fields.Many2One(Time, name='IssueTime', namespace='cbc')
    
    period = fields.Many2One(Period, name='InvoicePeriod', namespace='cac')

    supplier = fields.Many2One(AccountingSupplierParty, namespace='cac')
    customer = fields.Many2One(AccountingCustomerParty, namespace='cac')
    legal_monetary_total = fields.Many2One(LegalMonetaryTotal, namespace='cac')
    lines = fields.One2Many(InvoiceLine, namespace='cac')
    
    taxtotal_01 = fields.Many2One(TaxTotal)
    taxtotal_04 = fields.Many2One(TaxTotal)
    taxtotal_03 = fields.Many2One(TaxTotal)

    def __setup__(self):
        self._namespace_prefix = 'fe'
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

    def get_dian_extension(self, name, _value):
        return self._ubl_extensions.dian

    def to_xml(self, **kw):
        # al generar documento el namespace
        # se hace respecto a la raiz
        return super().to_xml(**kw)\
            .replace("fe:", "")\
            .replace("xmlns:fe", "xmlns")
