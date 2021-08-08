import facho.model as model
import facho.model.fields as fields
from .common import *

class SoftwareProvider(model.Model):
    __name__ = 'SoftwareProvider'

    provider_id = fields.Many2One(Element, name='ProviderID', namespace='sts')
    software_id = fields.Many2One(Element, name='SoftwareID', namespace='sts')

class InvoiceSource(model.Model):
    __name__ = 'InvoiceSource'

    identification_code = fields.Many2One(Element, name='IdentificationCode', namespace='sts', default='CO')
    
class AuthorizedInvoices(model.Model):
    __name__ = 'AuthorizedInvoices'

    prefix = fields.Many2One(Element, name='Prefix', namespace='sts')
    from_range = fields.Many2One(Element, name='From', namespace='sts')
    to_range = fields.Many2One(Element, name='To', namespace='sts')
    
class InvoiceControl(model.Model):
    __name__ = 'InvoiceControl'

    authorization = fields.Many2One(Element, name='InvoiceAuthorization', namespace='sts')
    period = fields.Many2One(Period, name='AuthorizationPeriod', namespace='sts')
    invoices = fields.Many2One(AuthorizedInvoices, namespace='sts')
    
class DianExtensions(model.Model):
    __name__ = 'DianExtensions'

    software_security_code = fields.Many2One(Element, name='SoftwareSecurityCode', namespace='sts')
    software_provider = fields.Many2One(SoftwareProvider, namespace='sts')
    source = fields.Many2One(InvoiceSource, namespace='sts')
    control = fields.Many2One(InvoiceControl, namespace='sts')

