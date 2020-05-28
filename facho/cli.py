import sys
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
@click.option('--password')
@click.argument('filename', required=True)
@click.argument('zipfile', type=click.Path(exists=True))
def SendTestSetAsync(private_key, public_key, password, filename, zipfile):
    from facho.fe.client import dian
    
    client = dian.DianSignatureClient(private_key, public_key, password=password)
    resp = client.request(dian.SendTestSetAsync(
        filename, open(zipfile, 'r').read().encode('utf-8')
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
    params = module.params()
    xml = form.DIANInvoiceXML(invoice, **params)
    
    extensions = module.extensions(invoice)
    for extension in extensions:
        xml.add_extension(extension)
    
    if private_key:
        signer = fe.DianXMLExtensionSigner(private_key, passphrase=passphrase)
        xml.add_extension(signer)
        xml.attach_extensions()
    print(str(xml))

    
@click.group()
def main():
    pass

main.add_command(consultaResolucionesFacturacion)
main.add_command(SendTestSetAsync)
main.add_command(generate_invoice)
