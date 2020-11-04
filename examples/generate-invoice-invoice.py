import facho.fe.form as form
from facho.fe import fe
from datetime import datetime

def extensions(inv):
    nit = form.PartyIdentification('nit', '5', '31')
    security_code = fe.DianXMLExtensionSoftwareSecurityCode('id software', 'pin', inv.invoice_ident)
    authorization_provider = fe.DianXMLExtensionAuthorizationProvider()
    cufe = fe.DianXMLExtensionCUFE(inv, fe.DianXMLExtensionCUFE.AMBIENTE_PRUEBAS,
                                   'clave tecnica')
    software_provider = fe.DianXMLExtensionSoftwareProvider(nit, nit.dv, 'id software')
    inv_authorization = fe.DianXMLExtensionInvoiceAuthorization('invoice autorization',
                                                                datetime(2019, 1, 19),
                                                                datetime(2030, 1, 19),
                                                                'SETP', 990000001, 995000000)
    return [security_code, authorization_provider, cufe, software_provider, inv_authorization]


def invoice():
    inv = form.Invoice()
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('SETP990003033')
    inv.set_operation_type('10')
    inv.set_supplier(form.Party(
        legal_name = 'FACHO SOS',
        name = 'FACHO SOS',
        ident = form.PartyIdentification('900579212', '5', '31'),
        responsability_code = form.Responsability(['O-07', 'O-09', 'O-14', 'O-48']),
        responsability_regime_code = '48',
        organization_code = '1',
        email = "sdds@sd.com",
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    inv.set_customer(form.Party(
        legal_name = 'facho-customer',
        name = 'facho-customer',
        ident = form.PartyIdentification('999999999', '', '13'),
        responsability_code = form.Responsability(['R-99-PN']),
        responsability_regime_code = '49',
        organization_code = '2',
        email = "sdds@sd.com",
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    inv.set_payment_mean(form.PaymentMean(
        id = '1',
        code = '10',
        due_at = datetime.now(),
        payment_id = '1'
    ))
    inv.add_invoice_line(form.InvoiceLine(
        quantity = form.Quantity(1, '94'),
        description = 'producto facho',
        item = form.StandardItem('test', 9999),
        price = form.Price(
            amount = form.Amount(100.00),
            type_code = '01',
            type = 'x'
        ),
        tax = form.TaxTotal(
            subtotals = [
                form.TaxSubTotal(
                    percent = 19.00,
                )
            ]
        )
    ))
    return inv
