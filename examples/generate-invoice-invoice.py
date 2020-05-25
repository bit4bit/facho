import facho.fe.form as form
from facho.fe import fe
from datetime import datetime

def extensions(inv):
    security_code = fe.DianXMLExtensionSoftwareSecurityCode('', '123', inv.invoice_ident)
    return [security_code]

def invoice():
    inv = form.Invoice()
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('ABC123')
    inv.set_supplier(form.Party(
        name = 'facho-supplier',
        ident = 123,
        responsability_code = 'No aplica',
        organization_code = 'Persona Natural'
    ))
    inv.set_customer(form.Party(
        name = 'facho-customer',
        ident = 321,
        responsability_code = 'No aplica',
        organization_code = 'Persona Natural'
    ))
    inv.add_invoice_line(form.InvoiceLine(
        quantity = 1,
        description = 'producto facho',
        item_ident = 9999,
        price_amount = 100.0,
        tax = form.TaxTotal(
            tax_amount = 0.0,
            taxable_amount = 0.0,
            subtotals = [
                form.TaxSubTotal(
                    percent = 19.0,
                )
            ]
        )
    ))
    return inv
