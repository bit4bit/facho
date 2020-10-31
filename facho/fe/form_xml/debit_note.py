from .. import fe
from ..form import *
from .invoice import DIANInvoiceXML

__all__ = ['DIANDebitNoteXML']

class DIANDebitNoteXML(DIANInvoiceXML):
    """
    DianInvoiceXML mapea objeto form.Invoice a XML segun
    lo indicado para la facturacion electronica.
    """

    def __init__(self, invoice):
        super().__init__(invoice, 'DebitNote')

    def tag_document(fexml):
        return 'DebitNote'

    def tag_document_concilied(fexml):
        return 'Debited'

    #DIAN 1.7.-2020: DAU03
    def set_legal_monetary(fexml, invoice):
        fexml.set_element_amount('./cac:RequestedMonetaryTotal/cbc:LineExtensionAmount',
                                 invoice.invoice_legal_monetary_total.line_extension_amount)

        fexml.set_element_amount('./cac:RequestedMonetaryTotal/cbc:TaxExclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_exclusive_amount)

        fexml.set_element_amount('./cac:RequestedMonetaryTotal/cbc:TaxInclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_inclusive_amount)

        fexml.set_element_amount('./cac:RequestedMonetaryTotal/cbc:ChargeTotalAmount',
                                invoice.invoice_legal_monetary_total.charge_total_amount)

        fexml.set_element_amount('./cac:RequestedMonetaryTotal/cbc:PayableAmount',
                                invoice.invoice_legal_monetary_total.payable_amount)
