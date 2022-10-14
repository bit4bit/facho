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
        super(DIANCreditNoteXML, self).__init__(invoice, 'CreditNote')

    def tag_document(fexml):
        return 'CreditNote'

    def tag_document_concilied(fexml):
        return 'Credited'

    def post_attach_invoice(fexml, invoice):
        fexml.set_element('./cbc:ProfileID', 'DIAN 2.1: Nota Crédito de Factura Electrónica de Venta')
