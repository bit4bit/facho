from .. import fe
from ..form import *
from .support_document import DIANSupportDocumentXML

__all__ = ['DIANSupportDocumentCreditNoteXML']

class DIANSupportDocumentCreditNoteXML(DIANSupportDocumentXML):
    """
    DianInvoiceXML mapea objeto form.Invoice a XML segun
    lo indicado para la facturacion electronica.
    """

    def __init__(self, invoice):
        super(DIANSupportDocumentCreditNoteXML, self).__init__(invoice, 'CreditNote')        

    def tag_document(fexml):
        return 'CreditNote'

    def tag_document_concilied(fexml):
        return 'Credited'

