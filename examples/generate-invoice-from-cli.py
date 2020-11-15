# este archivo es un ejemplo para le generacion
# una factura de venta nacional usando el comando **facho**.
#
# ejemplo: facho generate-invoice generate-invoice-from-cli.py
#
# importar libreria de modelos
import facho.fe.form as form
import facho.fe.form_xml

# importar libreria extensiones xml para cumplir decreto
from facho.fe import fe

# importar otras necesarias
from datetime import datetime

# callback que retorna el modelado de documento electronico
# a generar
def invoice():
    # factura de venta nacional
    inv = form.NationalSalesInvoice()
    # asignar periodo de facturacion
    inv.set_period(datetime.now(), datetime.now())
    # asignar fecha de emision de la factura
    inv.set_issue(datetime.now())
    # asignar prefijo y numero del documento
    inv.set_ident('SETP990003033')
    # asignar tipo de operacion ver DIAN:6.1.5
    inv.set_operation_type('10')
    # asignar proveedor
    inv.set_supplier(form.Party(
        legal_name = 'FACHO SOS',
        name = 'FACHO SOS',
        ident = form.PartyIdentification('900579212', '5', '31'),
        # obligaciones del contribuyente ver DIAN:FAK26
        responsability_code = form.Responsability(['O-07', 'O-09', 'O-14', 'O-48']),
        # ver DIAN:FAJ28
        responsability_regime_code = '48',
        # tipo de organizacion juridica ver DIAN:6.2.3
        organization_code = '1',
        email = "sdds@sd.com",
        address = form.Address(
            name = '',
            street = '',
            city = form.City('05001', 'Medellín'),
            country = form.Country('CO', 'Colombia'),
            countrysubentity = form.CountrySubentity('05', 'Antioquia'))
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
            name = '',
            street = '',
            city = form.City('05001', 'Medellín'),
            country = form.Country('CO', 'Colombia'),
            countrysubentity = form.CountrySubentity('05', 'Antioquia'))
    ))
    # asignar metodo de pago
    inv.set_payment_mean(form.PaymentMean(
        # metodo de pago ver DIAN:3.4.1
        id = '1',
        # codigo correspondiente al medio de pago ver DIAN:3.4.2
        code = '10',
        # fecha de vencimiento de la factura
        due_at = datetime.now(),

        # identificador numerico
        payment_id = '1'
    ))
    # adicionar una linea al documento
    inv.add_invoice_line(form.InvoiceLine(
        quantity = form.Quantity(1, '94'),
        description = 'producto facho',
        # item general de codigo 999
        item = form.StandardItem('test', 9999),
        price = form.Price(
            # precio base del tiem
            amount = form.Amount(100.00),
            # ver DIAN:6.3.5.1
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

# callback que retonar las extensiones XML necesarias
# para que el documento final XML cumpla el decreto.
#
# muchos de los valores usados son obtenidos
# del servicio web de la DIAN.
def extensions(inv):
    security_code = fe.DianXMLExtensionSoftwareSecurityCode('id software', 'pin', inv.invoice_ident)
    authorization_provider = fe.DianXMLExtensionAuthorizationProvider()
    cufe = fe.DianXMLExtensionCUFE(inv, fe.DianXMLExtensionCUFE.AMBIENTE_PRUEBAS,
                                   'clave tecnica')
    nit = form.PartyIdentification('nit', '5', '31')
    software_provider = fe.DianXMLExtensionSoftwareProvider(nit, nit.dv, 'id software')
    inv_authorization = fe.DianXMLExtensionInvoiceAuthorization('invoice autorization',
                                                                datetime(2019, 1, 19),
                                                                datetime(2030, 1, 19),
                                                                'SETP', 990000001, 995000000)
    return [security_code, authorization_provider, cufe, software_provider, inv_authorization]


# callback con transformador a XML
def document_xml():
    return form_xml.DIANInvoiceXML
