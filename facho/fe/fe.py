# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from ..facho import FachoXML, FachoXMLExtension, LXMLBuilder
import uuid
import xmlsig
import xades
from datetime import datetime
import OpenSSL
import zipfile
import warnings
import hashlib
from contextlib import contextmanager
from .data.dian import codelist

SCHEME_AGENCY_ATTRS = {
    'schemeAgencyName': 'CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)',
    'schemeAgencyID': '195'
}


# RESOLUCION 0001: pagina 516
POLICY_ID = 'https://facturaelectronica.dian.gov.co/politicadefirma/v2/politicadefirmav2.pdf'
POLICY_NAME = u'Política de firma para facturas electrónicas de la República de Colombia.'


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
    'sig': 'http://www.w3.org/2000/09/xmldsig#',
}

from contextlib import contextmanager
@contextmanager
def mock_xades_policy():
    from mock import patch
    import os.path
    with patch('xades.policy.urllib.urlopen') as mock:
        class UrllibPolicyMock:
            def read(self):
                cur_dir = os.path.dirname(os.path.abspath(__file__))
                data_dir = os.path.join(cur_dir, 'data', 'dian')
                policy_file = os.path.join(data_dir, 'politicadefirmav2.pdf')
                with open(policy_file, 'rb') as f:
                    return f.read()

        mock.return_value = UrllibPolicyMock()
        yield

class FeXML(FachoXML):

    def __init__(self, root, namespace):

        super().__init__("{%s}%s" % (namespace, root),
                         nsmap=NAMESPACES)

        self._cn = root.rstrip('/')
        #self.find_or_create_element(self._cn)

    # MACHETE se elimina xml namespace fe
    def tostringMACHETE(self, **kw):
        return super().tostring(**kw)\
            .replace("fe:", "")\
            .replace("xmlns:fe", "xmlns")


class DianXMLExtensionCUFE(FachoXMLExtension):
    AMBIENTE_PRUEBAS = codelist.TipoAmbiente.by_name('Pruebas')['code']
    AMBIENTE_PRODUCCION = codelist.TipoAmbiente.by_name('Producción')['code']

    def __init__(self, invoice, tipo_ambiente = AMBIENTE_PRUEBAS, clave_tecnica = ''):
        self.tipo_ambiente = tipo_ambiente
        self.clave_tecnica = clave_tecnica
        self.invoice = invoice

    def _tipo_ambiente(self):
        return int(self.tipo_ambiente)

    def build(self, fachoxml):
        cufe = self._generate_cufe(self.invoice, fachoxml)
        fachoxml.set_element('/fe:Invoice/cbc:UUID', cufe,
                             schemeID=self.tipo_ambiente,
                             schemeName='CUFE-SHA384')
        fachoxml.set_element('/fe:Invoice/cbc:ProfileID', 'DIAN 2.1')
        fachoxml.set_element('/fe:Invoice/cbc:ProfileExecutionID', self._tipo_ambiente())
        #DIAN 1.7.-2020: FAB36
        fachoxml.set_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:QRCode',
                'https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey='+cufe)

    def issue_time(self, datetime_):
        return datetime_.strftime('%H:%M:%S-05:00')

    def issue_date(self, datetime_):
        return datetime_.strftime('%Y-%m-%d')

    def formatVars(self, invoice):
        NumFac = invoice.invoice_ident
        FecFac = self.issue_date(invoice.invoice_issue)
        HoraFac = self.issue_time(invoice.invoice_issue)
        # PAG 601
        ValorBruto = invoice.invoice_legal_monetary_total.line_extension_amount
        ValorTotalPagar = invoice.invoice_legal_monetary_total.payable_amount
        ValorImpuestoPara = {}
        ValorImpuesto1 = 0.0
        CodImpuesto1 = 1
        ValorImpuesto2 = 0.0
        CodImpuesto2 = 4
        ValorImpuesto3 = 0.0
        CodImpuesto3 = 3
        for invoice_line in invoice.invoice_lines:
            for subtotal in invoice_line.tax.subtotals:
                # TODO cual es la naturaleza de tax_scheme_ident?
                codigo_impuesto = int(subtotal.tax_scheme_ident)
                ValorImpuestoPara.setdefault(codigo_impuesto, 0.0)
                ValorImpuestoPara[codigo_impuesto] += subtotal.tax_amount

        NitOFE = invoice.invoice_supplier.ident
        NumAdq = invoice.invoice_customer.ident
        TipoAmb = self._tipo_ambiente()
        ClTec = str(self.clave_tecnica)

        return [
            '%s' % NumFac,
            '%s' % FecFac,
            '%s' % HoraFac,
            '%.02f' % ValorBruto,
            '%02d' % CodImpuesto1,
            '%.02f' % ValorImpuestoPara.get(CodImpuesto1, 0.0),
            '%02d' % CodImpuesto2,
            '%.02f' % ValorImpuestoPara.get(CodImpuesto2, 0.0),
            '%02d' % CodImpuesto3,
            '%.02f' % ValorImpuestoPara.get(CodImpuesto3, 0.0),
            '%.02f' % ValorTotalPagar,
            '%s' % NitOFE,
            '%s' % NumAdq,
            '%s' % ClTec,
            '%d' % TipoAmb,
        ]

    def _generate_cufe(self, invoice, fachoxml):
        formatVars = self.formatVars(invoice)
        cufe = "".join(formatVars)

        # crear hash...
        h = hashlib.sha384()
        h.update(cufe.encode('utf-8'))
        return h.hexdigest()


class DianXMLExtensionSoftwareProvider(FachoXMLExtension):
    # RESOLUCION 0004: pagina 108

    def __init__(self, nit, dv, id_software: str):
        self.nit = nit
        self.dv = dv
        self.id_software = id_software

    def build(self, fexml):
        software_provider = fexml.fragment('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareProvider')
        provider_id_attrs = SCHEME_AGENCY_ATTRS.copy()
        provider_id_attrs.update({'schemeID': self.dv})
        #DIAN 1.7.-2020: FAB23
        provider_id_attrs.update({'schemeName': '31'})
        software_provider.set_element('/sts:SoftwareProvider/sts:ProviderID', self.nit,
                                      **provider_id_attrs)
        software_provider.set_element('/sts:SoftwareProvider/sts:SoftwareID', self.id_software,
                                      **SCHEME_AGENCY_ATTRS)



class DianXMLExtensionSoftwareSecurityCode(FachoXMLExtension):
    # RESOLUCION 0001: pagina 535

    def __init__(self, id_software: str, pin: str, invoice_ident: str):
        self.id_software = id_software
        self.pin = pin
        self.invoice_ident = invoice_ident

    def build(self, fexml):
        dian_path = '/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareSecurityCode'
        code = str(self.id_software) + str(self.pin) + str(self.invoice_ident)
        m = hashlib.sha384()
        m.update(code.encode('utf-8'))
        fexml.set_element(dian_path, m.hexdigest())
        fexml.set_attributes(dian_path, **SCHEME_AGENCY_ATTRS)
        return '', []


class DianXMLExtensionSigner:

    def __init__(self, pkcs12_path, passphrase=None, mockpolicy=False):
        self._pkcs12_path = pkcs12_path
        self._passphrase = None
        self._mockpolicy = mockpolicy
        if passphrase:
            self._passphrase = passphrase.encode('utf-8')

    @classmethod
    def from_pkcs12(self, filepath, password=None):
        p12 = OpenSSL.crypto.load_pkcs12(open(filepath, 'rb').read(), password)

    def sign_xml_string(self, document):
        xml = LXMLBuilder.from_string(document)
        signature = self.sign_xml_element(xml)

        fachoxml = FachoXML(xml,nsmap=NAMESPACES)
        #DIAN 1.7.-2020: FAB01
        extcontent = fachoxml.builder.xpath(fachoxml.root, '/fe:Invoice/ext:UBLExtensions/ext:UBLExtension[2]/ext:ExtensionContent')
        fachoxml.append_element(extcontent, signature)

        return fachoxml.tostring(xml_declaration=True, encoding='UTF-8')

    def sign_xml_element(self, xml):
        id_uuid = str(uuid.uuid4())
        signature = xmlsig.template.create(
            xmlsig.constants.TransformInclC14N,
            xmlsig.constants.TransformRsaSha256,
            "xmlsig-%s" % (id_uuid),
        )
        xml.append(signature)


        ref = xmlsig.template.add_reference(
            signature, xmlsig.constants.TransformSha256, uri="", name="xmldsig-%s-ref0" % (id_uuid)
        )
        xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)

        id_keyinfo = "xmldsig-%s-KeyInfo" % (id_uuid)
        xmlsig.template.add_reference(
            signature, xmlsig.constants.TransformSha256, uri="#%s" % (id_keyinfo), name="xmldsig-%s-ref1" % (id_uuid),
        )
        ki = xmlsig.template.ensure_key_info(signature, name=id_keyinfo)
        data = xmlsig.template.add_x509_data(ki)
        xmlsig.template.x509_data_add_certificate(data)
        xmlsig.template.add_key_value(ki)

        qualifying = xades.template.create_qualifying_properties(signature, 'XadesObjects', 'xades')
        xades.utils.ensure_id(qualifying)

        id_props = "xmldsig-%s-signedprops" % (id_uuid)
        props_ref = xmlsig.template.add_reference(
            signature, xmlsig.constants.TransformSha256, uri="#%s" % (id_props),
            uri_type="http://uri.etsi.org/01903#SignedProperties"
        )
        xmlsig.template.add_transform(props_ref, xmlsig.constants.TransformInclC14N)

        # TODO assert with http://www.sic.gov.co/hora-legal-colombiana
        props = xades.template.create_signed_properties(qualifying, name=id_props, datetime=datetime.now())
        xades.template.add_claimed_role(props, "supplier")

        policy = xades.policy.GenericPolicyId(
            POLICY_ID,
            POLICY_NAME,
            xmlsig.constants.TransformSha256)
        ctx = xades.XAdESContext(policy)
        ctx.load_pkcs12(OpenSSL.crypto.load_pkcs12(open(self._pkcs12_path, 'rb').read(),
                                                   self._passphrase))

        if self._mockpolicy:
            with mock_xades_policy():
                ctx.sign(signature)
                ctx.verify(signature)
        else:
            ctx.sign(signature)
            ctx.verify(signature)
        #xmlsig take parent root
        xml.remove(signature)
        return signature

    def build(self, fachoxml):
        signature = self.sign_xml_element(fachoxml.root)
        extcontent = fachoxml.builder.xpath(fachoxml.root, '/fe:Invoice/ext:UBLExtensions/ext:UBLExtension[2]/ext:ExtensionContent')
        fachoxml.append_element(extcontent, signature)

class DianXMLExtensionAuthorizationProvider(FachoXMLExtension):
    # RESOLUCION 0004: pagina 176

    def build(self, fexml):
        dian_path = '/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:AuthorizationProvider/sts:AuthorizationProviderID'
        fexml.set_element(dian_path, '800197268')

        attrs = {'schemeID': '4', 'schemeName': '31'}
        attrs.update(SCHEME_AGENCY_ATTRS)
        fexml.set_attributes(dian_path, **attrs)



class DianXMLExtensionInvoiceAuthorization(FachoXMLExtension):
    # RESOLUCION 0004: pagina 106

    def __init__(self, authorization: str,
                 period_startdate: datetime, period_enddate: datetime,
                 prefix: str, from_: int, to: int):
        self.authorization = authorization
        self.period_startdate = period_startdate
        self.period_enddate = period_enddate
        self.prefix = prefix
        self.from_ = from_
        self.to = to

    def build(self, fexml):
        fexml.set_element('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceSource/cbc:IdentificationCode',
                          'CO',
                          #DIAN 1.7.-2020: FAB15
                          listAgencyID="6",
                          #DIAN 1.7.-2020: FAB16
                          listAgencyName="United Nations Economic Commission for Europe",
                          #DIAN 1.7.-2020: FAB17
                          listSchemeURI="urn:oasis:names:specification:ubl:codelist:gc:CountryIdentificationCode-2.1"
                          )

        invoice_control = fexml.fragment('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceControl')
        invoice_control.set_element('/sts:InvoiceControl/sts:InvoiceAuthorization', self.authorization)
        invoice_control.set_element('/sts:InvoiceControl/sts:AuthorizationPeriod/cbc:StartDate',
                                    self.period_startdate.strftime('%Y-%m-%d'))
        invoice_control.set_element('/sts:InvoiceControl/sts:AuthorizationPeriod/cbc:EndDate',
                                    self.period_enddate.strftime('%Y-%m-%d'))
        invoice_control.set_element('/sts:InvoiceControl/sts:AuthorizedInvoices/sts:Prefix',
                                    self.prefix)
        invoice_control.set_element('/sts:InvoiceControl/sts:AuthorizedInvoices/sts:From',
                                    self.from_)
        invoice_control.set_element('/sts:InvoiceControl/sts:AuthorizedInvoices/sts:To',
                                    self.to)



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


class DianXMLExtensionSignerVerifier:

    def __init__(self, pkcs12_path, passphrase=None, mockpolicy=False):
        self._pkcs12_path = pkcs12_path
        self._passphrase = None
        self._mockpolicy = mockpolicy
        if passphrase:
            self._passphrase = passphrase.encode('utf-8')

    def verify_string(self, document):
        xml = LXMLBuilder.from_string(document)
        fachoxml = FachoXML(xml,nsmap=NAMESPACES)

        signature = fachoxml.builder.xpath(fachoxml.root, '//ds:Signature')
        assert signature is not None

        signature.getparent().remove(signature)
        fachoxml.root.append(signature)

        ctx = xades.XAdESContext()
        ctx.load_pkcs12(OpenSSL.crypto.load_pkcs12(open(self._pkcs12_path, 'rb').read(),
                                                   self._passphrase))

        try:
            if self._mockpolicy:
                with mock_xades_policy():
                    ctx.verify(signature)
            else:
                ctx.verify(signature)
            return True
        except:
            return False
