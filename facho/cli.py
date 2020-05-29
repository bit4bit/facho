import sys
import base64

import click

import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

@click.command()
@click.option('--nit', required=True)
@click.option('--nit-proveedor', required=True)
@click.option('--id-software', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
def consultaResolucionesFacturacion(nit, nit_proveedor, id_software, username, password):
    from facho.fe.client import dian
    client_dian = dian.DianClient(username,
                                  password)
    resp = client_dian.request(dian.ConsultaResolucionesFacturacionPeticion(
        nit, nit_proveedor, id_software
    ))
    print(str(resp))

    
@click.command()
@click.option('--private-key', required=True)
@click.option('--public-key', required=True)
@click.option('--habilitacion/--produccion', default=False)
@click.option('--password')
@click.option('--test-setid', required=True)
@click.argument('filename', required=True)
@click.argument('zipfile', type=click.Path(exists=True))
def soap_send_test_set_async(private_key, public_key, habilitacion, password, test_setid, filename, zipfile):
    from facho.fe.client import dian
    
    client = dian.DianSignatureClient(private_key, public_key, password=password)
    req = dian.SendTestSetAsync
    if habilitacion:
        req = dian.Habilitacion.SendTestSetAsync
    resp = client.request(req(
        filename,
        open(zipfile, 'rb').read(),
        test_setid,
    ))
    print(resp)

@click.command()
@click.option('--private-key', required=True)
@click.option('--public-key', required=True)
@click.option('--habilitacion/--produccion', default=False)
@click.option('--password')
@click.argument('filename', required=True)
@click.argument('zipfile', type=click.Path(exists=True))
def soap_send_bill_async(private_key, public_key, habilitacion, password, filename, zipfile):
    from facho.fe.client import dian
    
    client = dian.DianSignatureClient(private_key, public_key, password=password)
    req = dian.SendBillAsync
    if habilitacion:
        req = dian.Habilitacion.SendBillAsync
    resp = client.request(req(
        filename,
        open(zipfile, 'rb').read()
    ))
    print(resp)

@click.command()
@click.option('--private-key', required=True)
@click.option('--public-key', required=True)
@click.option('--habilitacion/--produccion', default=False)
@click.option('--password')
@click.argument('filename', required=True)
@click.argument('zipfile', type=click.Path(exists=True))
def soap_send_bill_sync(private_key, public_key, habilitacion, password, filename, zipfile):
    from facho.fe.client import dian
    
    client = dian.DianSignatureClient(private_key, public_key, password=password)
    req = dian.SendBillSync
    if habilitacion:
        req = dian.Habilitacion.SendBillSync
    resp = client.request(req(
        filename,
        open(zipfile, 'rb').read()
    ))
    print(resp)

@click.command()
@click.option('--private-key', required=True)
@click.option('--public-key', required=True)
@click.option('--habilitacion/--produccion', default=False)
@click.option('--password')
@click.option('--track-id', required=True)
def soap_get_status_zip(private_key, public_key, habilitacion, password, track_id):
    from facho.fe.client import dian
    
    client = dian.DianSignatureClient(private_key, public_key, password=password)
    req = dian.GetStatusZip
    if habilitacion:
        req = dian.Habilitacion.GetStatusZip
    resp = client.request(req(
        trackId = track_id
    ))
    print(resp)

@click.command()
@click.option('--private-key', required=True)
@click.option('--public-key', required=True)
@click.option('--habilitacion/--produccion', default=False)
@click.option('--password')
@click.option('--track-id', required=True)
def soap_get_status(private_key, public_key, habilitacion, password, track_id):
    from facho.fe.client import dian
    
    client = dian.DianSignatureClient(private_key, public_key, password=password)
    req = dian.GetStatus
    if habilitacion:
        req = dian.Habilitacion.GetStatus
    resp = client.request(req(
        trackId = track_id
    ))
    print(resp)

@click.command()
@click.option('--private-key', type=click.Path(exists=True))
@click.option('--passphrase')
@click.argument('scriptname', type=click.Path(exists=True), required=True)
def generate_invoice(private_key, passphrase, scriptname):
    """
    imprime xml en pantalla.
    SCRIPTNAME espera 
     def invoice() -> form.Invoice
     def extensions(form.Invoice): -> List[facho.FachoXMLExtension]
    """
    import importlib.util
    
    spec = importlib.util.spec_from_file_location('invoice', scriptname)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    import facho.fe.form as form
    from facho import fe

    invoice = module.invoice()
    invoice.calculate()
    xml = form.DIANInvoiceXML(invoice)
    
    extensions = module.extensions(invoice)
    for extension in extensions:
        xml.add_extension(extension)
    
    if private_key:
        signer = fe.DianXMLExtensionSigner(private_key, passphrase=passphrase)
        xml.add_extension(signer)
    print(xml.tostring(xml_declaration=True))

    
@click.group()
def main():
    pass

main.add_command(consultaResolucionesFacturacion)
main.add_command(soap_send_test_set_async)
main.add_command(soap_send_bill_async)
main.add_command(soap_send_bill_sync)
main.add_command(soap_get_status)
main.add_command(soap_get_status_zip)
main.add_command(generate_invoice)
