from .. import fe
from ..form import *
from .invoice import DIANInvoiceXML

__all__ = ['DIANCreditNoteXML']

class DIANCreditNoteXML(DIANInvoiceXML):
    """
    DianInvoiceXML mapea objeto form.Invoice a XML segun
    lo indicado para la facturacion electronica.
    """

    def __init__(self, invoice):
        super().__init__('CreditNote', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')

    def tag_document(fexml):
        return 'CreditNote'
    
    def tag_document_concilied(fexml):
        return 'Credited'

    def document_type_code(fexml):
        return codelist.TipoDocumento.by_name('Nota Crédito')['code']
