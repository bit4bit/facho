# este archivo es un ejemplo para le generacion
# una factura de venta nacional usando el comando **facho**.
#
# ejemplo: facho generate-invoice generate-invoice-from-cli.py
#
# importar libreria de modelos
from facho.fe import form
from facho.fe import form_xml

# importar libreria extensiones xml para cumplir decreto
from facho.fe import fe

# importar otras necesarias
from datetime import datetime, date

# Datos del fomulario del SET de pruebas
INVOICE_AUTHORIZATION = '181360000001' #Número suministrado por la Dian en el momento de la creación del SET de Pruebas  
ID_SOFTWARE = '57bcb6d1-c591-5a90-b80a-cb030ec91440' #Id suministrado por la Dian en el momento de la creación del SET de Pruebas  
PIN = '19642' #Número creado por la empresa para poder crear el SET de pruebas
CLAVE_TECNICA = 'fc9eac422eba16e21ffd8c5f94b3f30a6e38162d' ##Id suministrado por la Dian en el momento de la creación del SET de Pruebas  


# callback que retonar las extensiones XML necesarias
# para que el documento final XML cumpla el decreto.
#
# muchos de los valores usados son obtenidos
# del servicio web de la DIAN.
def extensions(inv):
    security_code = fe.DianXMLExtensionSoftwareSecurityCode(ID_SOFTWARE, PIN, inv.invoice_ident)
    authorization_provider = fe.DianXMLExtensionAuthorizationProvider()
    cufe = fe.DianXMLExtensionCUFE(inv, CLAVE_TECNICA, fe.AMBIENTE_PRUEBAS)
    software_provider = fe.DianXMLExtensionSoftwareProvider('nit_empresa', 'dígito_verificación', ID_SOFTWARE)
    inv_authorization = fe.DianXMLExtensionInvoiceAuthorization(INVOICE_AUTHORIZATION,
                                                                datetime(2019, 1, 19),#Datos toamdos de 
                                                                datetime(2030, 1, 19),#la configuración 
                                                                'SETP', 990000000, 995000000)#del SET de pruebas
    return [security_code, authorization_provider, cufe, software_provider, inv_authorization]

def invoice():
    # factura de venta nacional
    inv = form.Invoice('01')
    # asignar periodo de facturacion
    inv.set_period(datetime.now(), datetime.now())
    # asignar fecha de emision de la factura
    inv.set_issue(datetime.now())
    # asignar prefijo y numero del documento
    inv.set_ident('SETP990000008')
    # asignar tipo de operacion ver DIAN:6.1.5
    inv.set_operation_type('10')
    inv.set_supplier(form.Party(
        legal_name = 'Nombre registrado de la empresa',
        name = 'Nombre comercial o él mismo nombre registrado',
        ident = form.PartyIdentification('nit_empresa', 'digito_verificación', '31'),
        # obligaciones del contribuyente ver DIAN:FAK26
        responsability_code = form.Responsability(['O-07', 'O-14', 'O-48']),
        # ver DIAN:FAJ28
        responsability_regime_code = '48',
        # tipo de organizacion juridica ver DIAN:6.2.3
        organization_code = '1',
        email = "correoempresa@correoempresa.correo",
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia')),
    ))
    #Tercero a quien se le factura
    inv.set_customer(form.Party(
        legal_name = 'consumidor final',
        name = 'consumidor final',
        ident = form.PartyIdentification('222222222222', '', '13'),
        responsability_code = form.Responsability(['R-99-PN']),
        responsability_regime_code = '49',
        organization_code = '2',
        email = "consumidor_final0final.final",
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia')),
		#tax_scheme = form.TaxScheme('01', 'IVA')
    ))
    # asignar metodo de pago    
    inv.set_payment_mean(form.PaymentMean(
        # metodo de pago ver DIAN:3.4.1
        id = '1',
        # codigo correspondiente al medio de pago ver DIAN:3.4.2
        code = '20',
        # fecha de vencimiento de la factura        
        due_at = datetime.now(),
        # identificador numerico
        payment_id = '2'
    ))
    # adicionar una linea al documento
    inv.add_invoice_line(form.InvoiceLine(
        quantity = form.Quantity(int(20.5), '94'),
        # item general de codigo 999
        description = 'productO3',
        item = form.StandardItem('test', 9999),
        price = form.Price(
            # precio base del item (sin iva)
            amount = form.Amount(200.00),
            # ver DIAN:6.3.5.1
            type_code = '01',
            type = 'x'
        ),
        tax = form.TaxTotal(
            subtotals = [
                form.TaxSubTotal(
                    percent = 19.00,
                    scheme=form.TaxScheme('01')
                )
            ]
        )
    ))
    return inv

def document_xml():
    return form_xml.DIANInvoiceXML
