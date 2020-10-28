# -*- coding: utf-8 -*-
import sys
import base64
import warnings

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

def disable_ssl():
    # MACHETE
    import ssl
    if getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context
        warnings.warn("be sure!! ssl disable")
    else:
        warnings.warn("can't disable ssl")


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

    print("StatusCode:", resp.StatusCode)
    print("StatusDescription:", resp.StatusDescription)
    print("===ERRORES NOTIFICADOS====")
    for error_msg in resp.ErrorMessage:
        print("*", error_msg)


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
@click.option('--private-key', required=True)
@click.option('--public-key', required=True)
@click.option('--habilitacion/--produccion', default=False)
@click.option('--password')
@click.option('--nit', required=True)
@click.option('--nit-proveedor', required=True)
@click.option('--id-software', required=True)
def soap_get_numbering_range(private_key,
                             public_key,
                             habilitacion,
                             password,
                             nit, nit_proveedor, id_software):
    from facho.fe.client import dian

    client = dian.DianSignatureClient(private_key, public_key, password=password)
    req = dian.GetNumberingRange
    if habilitacion:
        req = dian.Habilitacion.GetNumberingRange
    resp = client.request(req(
        nit, nit_proveedor, id_software
    ))
    print(resp)

@click.command()
@click.argument('invoice_path')
def validate_invoice(invoice_path):
    warnings.warn("!! NO APROBADO FUNCIONAMIENTO")

    from facho.fe.data.dian import XSD
    content = open(invoice_path, 'r').read()
    # TODO donde ubicar esta responsabilidad?
    # esto es requerido por el XSD de la DIAN
    content = content.replace(
        'xmlns:fe="http://www.dian.gov.co/contratos/facturaelectronica/v1"',
        'xmlns:fe="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"'
    )
    XSD.validate(content, XSD.UBLInvoice)


@click.command()
@click.option('--private-key', type=click.Path(exists=True))
@click.option('--passphrase')
@click.option('--ssl/--no-ssl', default=False)
@click.option('--use-cache-policy/--no-use-cache-policy', default=False)
@click.argument('xmlfile', type=click.Path(exists=True), required=True)
@click.argument('output', required=True)
def sign_xml(private_key, passphrase, xmlfile, ssl=True, use_cache_policy=False, output=None):
    if not ssl:
        disable_ssl()

    from facho import fe
    if use_cache_policy:
        warnings.warn("xades using cache policy")

    signer = fe.DianXMLExtensionSigner(private_key, passphrase=passphrase, mockpolicy=use_cache_policy)
    document = open(xmlfile, 'r').read().encode('utf-8')
    with open(output, 'w') as f:
        f.write(signer.sign_xml_string(document))

@click.command()
@click.option('--private-key', type=click.Path(exists=True))
@click.option('--generate/--validate', default=False)
@click.option('--passphrase')
@click.option('--ssl/--no-ssl', default=False)
@click.option('--sign/--no-sign', default=False)
@click.option('--use-cache-policy/--no-use-cache-policy', default=False)
@click.argument('scriptname', type=click.Path(exists=True), required=True)
@click.argument('output', required=True)
def generate_invoice(private_key, passphrase, scriptname, generate=False, ssl=True, sign=False, use_cache_policy=False, output=None):
    """
    imprime xml en pantalla.
    SCRIPTNAME espera
     def invoice() -> form.Invoice
     def extensions(form.Invoice): -> List[facho.FachoXMLExtension]
    """

    if not ssl:
        disable_ssl()

    import importlib.util

    spec = importlib.util.spec_from_file_location('invoice', scriptname)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    import facho.fe.form as form
    from facho.fe.form_xml import DIANInvoiceXML, DIANWriteSigned,DIANWrite
    from facho import fe

    try:
        invoice_xml = module.document_xml()
    except AttributeError:
        invoice_xml = DIANInvoiceXML

    print("Using document xml:", invoice_xml)
    invoice = module.invoice()
    invoice.calculate()

    if generate:
        xml = invoice_xml(invoice)

        extensions = module.extensions(invoice)
        for extension in extensions:
            xml.add_extension(extension)

        if sign:
            DIANWriteSigned(xml, output, private_key, passphrase, use_cache_policy)
        else:
            DIANWrite(xml, output)


@click.command()
@click.option('--private-key', type=click.Path(exists=True))
@click.option('--passphrase')
@click.option('--ssl/--no-ssl', default=False)
@click.option('--use-cache-policy/--no-use-cache-policy', default=False)
@click.argument('xmlfile', type=click.Path(exists=True), required=True)
def sign_verify_xml(private_key, passphrase, xmlfile, ssl=True, use_cache_policy=False, output=None):
    if not ssl:
        disable_ssl()

    from facho.fe import fe
    if use_cache_policy:
        warnings.warn("xades using cache policy")

    print("THIS ONLY WORKS FOR DOCUMENTS GENERATE WITH FACHO")
    signer = fe.DianXMLExtensionSignerVerifier(private_key, passphrase=passphrase, mockpolicy=use_cache_policy)
    document = open(xmlfile, 'r').read().encode('utf-8')

    if signer.verify_string(document):
        print("+OK")
    else:
        print("-INVALID")

@click.group()
def main():
    pass

main.add_command(consultaResolucionesFacturacion)
main.add_command(soap_send_test_set_async)
main.add_command(soap_send_bill_async)
main.add_command(soap_send_bill_sync)
main.add_command(soap_get_status)
main.add_command(soap_get_status_zip)
main.add_command(soap_get_numbering_range)
main.add_command(generate_invoice)
main.add_command(validate_invoice)
main.add_command(sign_xml)
main.add_command(sign_verify_xml)
