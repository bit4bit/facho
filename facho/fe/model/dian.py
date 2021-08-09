import facho.model as model
import facho.model.fields as fields
from .common import *

class DIANElement(Element):
    """
    Elemento que contiene atributos por defecto.
    
    Puede extender esta clase y modificar los atributos nuevamente
    """
    __name__ = 'DIANElement'
    
    scheme_id = fields.Attribute('schemeID', default='4')
    scheme_name = fields.Attribute('schemeName', default='31')
    scheme_agency_name = fields.Attribute('schemeAgencyName', default='CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)')
    scheme_agency_id = fields.Attribute('schemeAgencyID', default='195')
    
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

class AuthorizationProvider(model.Model):
    __name__ = 'AuthorizationProvider'


    id = fields.Many2One(DIANElement, name='AuthorizationProviderID', namespace='sts', default='800197268')
    
class DianExtensions(model.Model):
    __name__ = 'DianExtensions'

    authorization_provider = fields.Many2One(AuthorizationProvider, namespace='sts', create=True)

    software_security_code = fields.Many2One(Element, name='SoftwareSecurityCode', namespace='sts')
    software_provider = fields.Many2One(SoftwareProvider, namespace='sts')
    source = fields.Many2One(InvoiceSource, namespace='sts')
    control = fields.Many2One(InvoiceControl, namespace='sts')

