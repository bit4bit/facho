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
from . import form
from collections import defaultdict
from pathlib import Path

AMBIENTE_PRUEBAS = codelist.TipoAmbiente.by_name('Pruebas')['code']
AMBIENTE_PRODUCCION = codelist.TipoAmbiente.by_name('Producción')['code']


SCHEME_AGENCY_ATTRS = {
    'schemeAgencyName': 'CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)',
    'schemeAgencyID': '195'
}


pwd = Path(__file__).parent
# RESOLUCION 0001: pagina 516
POLICY_ID = 'file://'+str(pwd)+'/data/dian/politicadefirmav2.pdf'
POLICY_NAME = u'Política de firma para facturas electrónicas de la República de Colombia.'


NAMESPACES = {
    'facho': 'http://git.disroot.org/Etrivial/facho',
    'fe': 'http://www.dian.gov.co/contratos/facturaelectronica/v1',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cdt': 'urn:DocumentInformation:names:specification:ubl:colombia:schema:xsd:DocumentInformationAggregateComponents-1',
    'clm54217': 'urn:un:unece:uncefact:codelist:specification:54217:2001',
    'clmIANAMIMEMediaType': 'urn:un:unece:uncefact:codelist:specification:IANAMIMEMediaType:2003',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'qdt': 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
    'udt': 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'sig': 'http://www.w3.org/2000/09/xmldsig#',
}

def fe_from_string(document: str) -> FachoXML:
    return FeXML.from_string(document)

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

    @classmethod
    def from_string(cls, document: str) -> 'FeXML':
        return super().from_string(document, namespaces=NAMESPACES)
    
    def tostring(self, **kw):
        return super().tostring(**kw)\
            .replace("fe:", "")\
            .replace("xmlns:fe", "xmlns")



class DianXMLExtensionCUDFE(FachoXMLExtension):

    def __init__(self, invoice, tipo_ambiente = AMBIENTE_PRUEBAS):
        self.tipo_ambiente = tipo_ambiente
        self.invoice = invoice

    def _tipo_ambiente_int(self):
        return int(self.tipo_ambiente)

    def formatVars(self, invoice):
        raise NotImplementedError()

    def schemeName(self):
        raise NotImplementedError()

    def _get_qrcode(self, cufe):
        url_for = {
            AMBIENTE_PRUEBAS: 'https://catalogo-vpfe-hab.dian.gov.co/document/searchqr?documentkey=',
            AMBIENTE_PRODUCCION: 'https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey='
        }
        return url_for[self.tipo_ambiente] + cufe

    def build(self, fachoxml):
        cufe = self._generate_cufe()
        fachoxml.set_element('./cbc:UUID', cufe,
                             schemeID=self.tipo_ambiente,
                             schemeName=self.schemeName())
        fachoxml.set_element('./cbc:ProfileID', 'DIAN 2.1')
        fachoxml.set_element('./cbc:ProfileExecutionID', self._tipo_ambiente_int())
        #DIAN 1.7.-2020: FAB36
        fachoxml.set_element('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:QRCode',
                self._get_qrcode(cufe))

    def issue_time(self, datetime_):
        return datetime_.strftime('%H:%M:%S-05:00')

    def issue_date(self, datetime_):
        return datetime_.strftime('%Y-%m-%d')

    def buildVars(self):
        invoice = self.invoice
        build_vars = {}
        build_vars['NumFac'] = invoice.invoice_ident
        build_vars['FecFac'] = self.issue_date(invoice.invoice_issue)
        build_vars['HoraFac'] = self.issue_time(invoice.invoice_issue)
        # PAG 601
        build_vars['ValorBruto'] = invoice.invoice_legal_monetary_total.line_extension_amount
        build_vars['ValorTotalPagar'] = invoice.invoice_legal_monetary_total.payable_amount
        ValorImpuestoPara = defaultdict(lambda: form.Amount(0.0))
        build_vars['CodImpuesto1'] = '01'
        build_vars['CodImpuesto2'] = '04'
        build_vars['CodImpuesto3'] = '03'
        for invoice_line in invoice.invoice_lines:
            for subtotal in invoice_line.tax.subtotals:
                if subtotal.scheme is not None:
                    # TODO cual es la naturaleza de tax_scheme_ident?
                    codigo_impuesto = subtotal.scheme.code
                    ValorImpuestoPara.setdefault(codigo_impuesto, form.Amount(0.0))
                    ValorImpuestoPara[codigo_impuesto] += subtotal.tax_amount

        build_vars['ValorImpuestoPara'] = ValorImpuestoPara
        build_vars['NitOFE'] = invoice.invoice_supplier.ident
        build_vars['NumAdq'] = invoice.invoice_customer.ident
        build_vars['TipoAmb'] = self._tipo_ambiente_int()

        return build_vars

    def _generate_cufe(self):
        cufe = "".join(self.formatVars())

        # crear hash...
        h = hashlib.sha384()
        h.update(cufe.encode('utf-8'))
        return h.hexdigest()


class DianXMLExtensionCUFE(DianXMLExtensionCUDFE):
    def __init__(self, invoice,  clave_tecnica = '', tipo_ambiente = AMBIENTE_PRUEBAS):
        self.tipo_ambiente = tipo_ambiente
        self.clave_tecnica = clave_tecnica
        self.invoice = invoice

    def schemeName(self):
        return 'CUFE-SHA384'

    def buildVars(self):
        build_vars = super().buildVars()
        build_vars['ClTec'] = str(self.clave_tecnica)
        return build_vars

    def formatVars(self):
        build_vars = self.buildVars()
        CodImpuesto1 = build_vars['CodImpuesto1']
        CodImpuesto2 = build_vars['CodImpuesto2']
        CodImpuesto3 = build_vars['CodImpuesto3']
        return [
            '%s' % build_vars['NumFac'],
            '%s' % build_vars['FecFac'],
            '%s' % build_vars['HoraFac'],
            form.Amount(build_vars['ValorBruto']).truncate_as_string(2),
            CodImpuesto1,
            build_vars['ValorImpuestoPara'].get(CodImpuesto1, form.Amount(0.0)).truncate_as_string(2),
            CodImpuesto2,
            build_vars['ValorImpuestoPara'].get(CodImpuesto2, form.Amount(0.0)).truncate_as_string(2),
            CodImpuesto3,
            build_vars['ValorImpuestoPara'].get(CodImpuesto3, form.Amount(0.0)).truncate_as_string(2),
            build_vars['ValorTotalPagar'].truncate_as_string(2),
            '%s' % build_vars['NitOFE'],
            '%s' % build_vars['NumAdq'],
            '%s' % build_vars['ClTec'],
            '%d' % build_vars['TipoAmb'],
        ]

class DianXMLExtensionCUDE(DianXMLExtensionCUDFE):
    def __init__(self, invoice, software_pin, tipo_ambiente = AMBIENTE_PRUEBAS):
        self.tipo_ambiente = tipo_ambiente
        self.software_pin = software_pin
        self.invoice = invoice

    def schemeName(self):
        return 'CUDE-SHA384'

    def buildVars(self):
        build_vars = super().buildVars()
        build_vars['Software-PIN'] = str(self.software_pin)
        return build_vars

    def formatVars(self):
        build_vars = self.buildVars()
        CodImpuesto1 = build_vars['CodImpuesto1']
        CodImpuesto2 = build_vars['CodImpuesto2']
        CodImpuesto3 = build_vars['CodImpuesto3']
        return [
            '%s' % build_vars['NumFac'],
            '%s' % build_vars['FecFac'],
            '%s' % build_vars['HoraFac'],
            form.Amount(build_vars['ValorBruto']).truncate_as_string(2),
            CodImpuesto1,
            form.Amount(build_vars['ValorImpuestoPara'].get(CodImpuesto1, 0.0)).truncate_as_string(2),
            CodImpuesto2,
            form.Amount(build_vars['ValorImpuestoPara'].get(CodImpuesto2, 0.0)).truncate_as_string(2),
            CodImpuesto3,
            form.Amount(build_vars['ValorImpuestoPara'].get(CodImpuesto3, 0.0)).truncate_as_string(2),
            form.Amount(build_vars['ValorTotalPagar']).truncate_as_string(2),
            '%s' % build_vars['NitOFE'],
            '%s' % build_vars['NumAdq'],
            '%s' % build_vars['Software-PIN'],
            '%d' % build_vars['TipoAmb'],
        ]

class DianXMLExtensionSoftwareProvider(FachoXMLExtension):
    # RESOLUCION 0004: pagina 108

    def __init__(self, nit, dv, id_software: str):
        self.nit = nit
        self.dv = dv
        self.id_software = id_software

    def build(self, fexml):
        software_provider = fexml.fragment('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareProvider')
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
        dian_path = './ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareSecurityCode'
        code = str(self.id_software) + str(self.pin) + str(self.invoice_ident)
        m = hashlib.sha384()
        m.update(code.encode('utf-8'))
        fexml.set_element(dian_path, m.hexdigest())
        fexml.set_attributes(dian_path, **SCHEME_AGENCY_ATTRS)
        return '', []


class DianXMLExtensionSigner:

    def __init__(self, pkcs12_path, passphrase=None, mockpolicy=False):
        self._pkcs12_data = open(pkcs12_path, 'rb').read()
        self._passphrase = None
        self._mockpolicy = mockpolicy
        if passphrase:
            self._passphrase = passphrase.encode('utf-8')

    @classmethod
    def from_bytes(cls, data, passphrase=None, mockpolicy=False):
        self = cls.__new__(cls)
        
        self._pkcs12_data = data
        self._passphrase = None
        self._mockpolicy = mockpolicy
        if passphrase:
            self._passphrase = passphrase.encode('utf-8')
            
        return self
    
    def sign_xml_string(self, document):
        xml = LXMLBuilder.from_string(document)
        signature = self.sign_xml_element(xml)

        fachoxml = FachoXML(xml,nsmap=NAMESPACES)
        #DIAN 1.7.-2020: FAB01
        extcontent = fachoxml.builder.xpath(fachoxml.root, './ext:UBLExtensions/ext:UBLExtension[2]/ext:ExtensionContent')
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
        ctx.load_pkcs12(OpenSSL.crypto.load_pkcs12(self._pkcs12_data,
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
        extcontent = fachoxml.builder.xpath(fachoxml.root, './ext:UBLExtensions/ext:UBLExtension[2]/ext:ExtensionContent')
        fachoxml.append_element(extcontent, signature)

        
class DianXMLExtensionAuthorizationProvider(FachoXMLExtension):
    # RESOLUCION 0004: pagina 176

    def build(self, fexml):
        attrs = {'schemeID': '4', 'schemeName': '31'}
        attrs.update(SCHEME_AGENCY_ATTRS)
        
        authorization_provider = fexml.fragment('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:AuthorizationProvider')
        authorization_provider.set_element('./sts:AuthorizationProviderID',
                                           '800197268',
                                           **attrs)



class DianXMLExtensionInvoiceSource(FachoXMLExtension):
    # CAB13
    def build(self, fexml):
        dian_path = '/fe:CreditNote/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceSource/cbc:IdentificationCode'
        fexml.set_element(dian_path, 'CO',
                          listAgencyID="6",
                          listAgencyName="United Nations Economic Commission for Europe",
                          listSchemeURI="urn:oasis:names:specification:ubl:codelist:gc:CountryIdentificationCode-2.1")


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
        invoice_control = fexml.fragment('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceControl')
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

        fexml.set_element('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceSource/cbc:IdentificationCode',
                          'CO',
                          #DIAN 1.7.-2020: FAB15
                          listAgencyID="6",
                          #DIAN 1.7.-2020: FAB16
                          listAgencyName="United Nations Economic Commission for Europe",
                          #DIAN 1.7.-2020: FAB17
                          listSchemeURI="urn:oasis:names:specification:ubl:codelist:gc:CountryIdentificationCode-2.1"
                          )



class DianZIP:

    # RESOLUCION 0001: pagina 540
    MAX_FILES = 50

    def __init__(self, file_like):
        self.zipfile = zipfile.ZipFile(file_like, mode='w', compression=zipfile.ZIP_DEFLATED)
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

    def __init__(self, pkcs12_path_or_bytes, passphrase=None, mockpolicy=False):
        self._pkcs12_path_or_bytes = pkcs12_path_or_bytes
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

        pkcs12_data = self._pkcs12_path_or_bytes
        if isinstance(self._pkcs12_path_or_bytes, str):
            pkcs12_data = open(self._pkcs12_path_or_bytes, 'rb').read()

        ctx.load_pkcs12(OpenSSL.crypto.load_pkcs12(pkcs12_data,
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
