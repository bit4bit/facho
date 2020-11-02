"""
utilidades
"""

from .. import form
from ..fe import fe_from_string
from datetime import datetime

def billing_reference(xmldocument: str, klass: form.BillingReference) -> form.BillingReference:
    """
    construye BillingReference desde XMLDOCUMENT
    usando KLASS como clase.
    """
    if not issubclass(klass, form.BillingReference):
        raise TypeError('klass expected subclass of BillingReference')
    
    fachoxml = fe_from_string(xmldocument)
    
    uid = fachoxml.get_element_text('./cbc:ID')
    uuid = fachoxml.get_element_text('./cbc:UUID')
    issue_date = fachoxml.get_element_text('./cbc:IssueDate')
    date = datetime.strptime(issue_date, '%Y-%m-%d')
    return klass(ident=uid, uuid=uuid, date=date)
