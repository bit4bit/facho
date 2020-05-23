# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from ..facho import FachoXML
import xmlsig
import xades
from datetime import datetime
import OpenSSL
import zipfile
import warnings
import hashlib
from contextlib import contextmanager

NAMESPACES = {
    'fe': 'http://www.dian.gov.co/contratos/facturaelectronica/v1',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cdt': 'urn:DocumentInformation:names:specification:ubl:colombia:schema:xsd:DocumentInformationAggregateComponents-1',
    'clm54217': 'urn:un:unece:uncefact:codelist:specification:54217:2001',
    'clmIANAMIMEMediaType': 'urn:un:unece:uncefact:codelist:specification:IANAMIMEMediaType:2003',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'qdt': 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2',
    'sts': 'http://www.dian.gov.co/contratos/facturaelectronica/v1/Structures',
    'udt': 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
}


class FeXML(FachoXML):

    def __init__(self, root, namespace):
        
        super().__init__("{%s}%s" % (namespace, root),
                         nsmap=NAMESPACES)

        self._cn = root.rstrip('/')
        #self.find_or_create_element(self._cn)


        
class DianXMLExtensionSigner:
    POLICY_ID = 'https://facturaelectronica.dian.gov.co/politicadefirma/v2/politicadefirmav2.pdf'
    POLICY_NAME = 'Dian'
    
    def __init__(self, pkcs12_path, passphrase=None):
        self._pkcs12_path = pkcs12_path
        self._passphrase = None
        if passphrase:
            self._passphrase = passphrase.encode('utf-8')

    @classmethod
    def from_pkcs12(self, filepath, password=None):
        p12 = OpenSSL.crypto.load_pkcs12(open(filepath, 'rb').read(), password)

    # return (xpath, xml.Element)
    def build(self, fachoxml):
        dian_path = '/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent'
        
        signature = xmlsig.template.create(
            xmlsig.constants.TransformInclC14N,
            xmlsig.constants.TransformRsaSha256,
            "Signature",
        )
        ref = xmlsig.template.add_reference(
            signature, xmlsig.constants.TransformSha256, uri="", name="R1"
        )
        xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)
        xmlsig.template.add_reference(
            signature, xmlsig.constants.TransformSha256, uri="#KI", name="RKI"
        )
        ki = xmlsig.template.ensure_key_info(signature, name="KI")
        data = xmlsig.template.add_x509_data(ki)
        xmlsig.template.x509_data_add_certificate(data)
        serial = xmlsig.template.x509_data_add_issuer_serial(data)
        xmlsig.template.x509_issuer_serial_add_issuer_name(serial)
        xmlsig.template.x509_issuer_serial_add_serial_number(serial)
        xmlsig.template.add_key_value(ki)
        qualifying = xades.template.create_qualifying_properties(signature)
        xades.utils.ensure_id(qualifying)
        xades.utils.ensure_id(qualifying)

        # TODO assert with http://www.sic.gov.co/hora-legal-colombiana
        props = xades.template.create_signed_properties(qualifying, datetime=datetime.now())
        xades.template.add_claimed_role(props, "supplier")
        #signed_do = xades.template.ensure_signed_data_object_properties(props)
        #xades.template.add_data_object_format(
        #    signed_do, "#R1",
        #    identifier=xades.ObjectIdentifier("Idenfitier0", "Description")
        #)
        #xades.template.add_commitment_type_indication(
        #    signed_do,
        #    xades.ObjectIdentifier("Idenfitier0", "Description"),
        #    qualifiers_type=["Tipo"],
        #)

        #xades.template.add_commitment_type_indication(
        #    signed_do,
        #    xades.ObjectIdentifier("Idenfitier1", references=["#R1"]),
        #    references=["#R1"],
        #)
        #xades.template.add_data_object_format(
        #    signed_do,
        #    "#RKI",
        #    description="Desc",
        #    mime_type="application/xml",
        #    encoding="UTF-8",
        #)

        fachoxml.root.append(signature)

        policy = xades.policy.GenericPolicyId(
            self.POLICY_ID,
            self.POLICY_NAME,
            xmlsig.constants.TransformSha256)
        ctx = xades.XAdESContext(policy)
        ctx.load_pkcs12(OpenSSL.crypto.load_pkcs12(open(self._pkcs12_path, 'rb').read(),
                                                   self._passphrase))

        ctx.sign(signature)
        ctx.verify(signature)
        #xmlsig take parent root
        fachoxml.root.remove(signature)
        
        return (dian_path, [signature])
        


class DianZIP:
    
    # RESOLUCION 0001: pagina 540
    MAX_FILES = 50
    
    def __init__(self, file_like):
        self.zipfile = zipfile.ZipFile(file_like, mode='w')
        self.num_files = 0

    def add_invoice_xml(self, name, xml_data):
        self.num_files += 1
        # TODO cual es la norma para los nombres de archivos?
        m = hashlib.sha256()
        m.update(name.encode('utf-8'))
        filename = m.hexdigest() + '.xml'
        with self.zipfile.open(filename, 'w') as fp:
            fp.write(xml_data.encode('utf-8'))

        return filename

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self.zipfile.close()
