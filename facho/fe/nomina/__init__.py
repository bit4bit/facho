#
# Para esta implementacion se usa BDD
# ver **test_nomina.py**.
#
# La idea en general es validar comportamiento desde el XML,
# creando las estructuras minimas necesaras.

from dataclasses import dataclass
import hashlib

from .. import fe
from .. import form
from ..data.dian import codelist

from .devengado import *
from .deduccion import *
from .trabajador import *
from .empleador import *
from .pago import *
from .lugar import Lugar

from .amount import Amount
from .exception import *

@dataclass
class NumeroSecuencia:
    consecutivo: int
    numero: str

    def apply(self, fragment):
        fragment.set_attributes('./NumeroSecuenciaXML',
                                # NIE011
                                Consecutivo=self.consecutivo,
                                # NIE012
                                Numero = self.numero)


@dataclass
class Proveedor:
    nit: str
    dv: int
    software_id: str
    software_sc: str

    def apply(self, fragment):
        fragment.set_attributes('./ProveedorXML',
                                # NIE017
                                NIT=self.nit,
                                # NIE018
                                DV=self.dv,
                                # NIE019
                                SoftwareID=self.software_id,
                                # NIE020
                                SoftwareSC=self.software_sc,
                                )

    def post_apply(self, fexml, fragment):
        cune_xpath = fexml.xpath_from_root('/InformacionGeneral')
        cune = fexml.get_element_attribute(cune_xpath, 'CUNE')
        codigo_qr = f"https://catalogo‐vpfe.dian.gov.co/document/searchqr?documentkey={cune}"
        fragment.set_attributes('./ProveedorXML',
                                CodigoQR=codigo_qr)
        
@dataclass
class Metadata:
    secuencia: NumeroSecuencia
    # NIE013, NIE014, NIE015, NIE016
    lugar_generacion: Lugar
    proveedor: Proveedor

    def apply(self, numero_secuencia_xml, lugar_generacion_xml, proveedor_xml):
        self.secuencia.apply(numero_secuencia_xml)
        self.lugar_generacion.apply(lugar_generacion_xml, './LugarGeneracionXML')
        self.proveedor.apply(proveedor_xml)

    def post_apply(self, fexml, numero_secuencia_xml, lugar_generacion_xml, proveedor_xml):
        self.proveedor.post_apply(fexml, proveedor_xml)
        
@dataclass
class PeriodoNomina:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.PeriodoNomina:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.PeriodoNomina[self.code]['name']

@dataclass
class TipoMoneda:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.TipoMoneda:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.TipoMoneda[self.code]['name']

@dataclass
class InformacionGeneral:
    class TIPO_AMBIENTE:
        pass

    # TABLA 5.1.1
    @dataclass
    class AMBIENTE_PRODUCCION(TIPO_AMBIENTE):
        valor: str = '1'
    @dataclass
    class AMBIENTE_PRUEBAS(TIPO_AMBIENTE):
        valor: str = '2'

    fecha_generacion: str
    hora_generacion: str
    periodo_nomina: PeriodoNomina
    tipo_moneda: TipoMoneda
    tipo_ambiente: TIPO_AMBIENTE
    software_pin: str

    def apply(self, fragment):
        fragment.set_attributes('./InformacionGeneral',
                                # NIE022
                                Version = 'V1.0: Documento Soporte de Pago de Nómina ElectrónicaV1.0',
                                # NIE023
                                Ambiente = self.tipo_ambiente.valor,
                                # NIE202
                                # TABLA 5.5.2
                                # TODO(bit4bit) solo NominaIndividual
                                TipoXML = '102',
                                # NIE024
                                CUNE = None,
                                # NIE025
                                EncripCUNE = 'SHA-384',
                                # NIE026
                                FechaGen = self.fecha_generacion,
                                # NIE027
                                HoraGen = self.hora_generacion,
                                # NIE029
                                PeriodoNomina = self.periodo_nomina.code,
                                # NIE030
                                TipoMoneda = self.tipo_moneda.code
                                # TODO(bit4bit) resto...
                                # .....
                                )

    def post_apply(self, fexml, fragment):
        # generar cune
        # ver 8.1.1.1
        xpaths = [
            fexml.xpath_from_root('/NumeroSecuenciaXML/@Numero'),
            fexml.xpath_from_root('/InformacionGeneral/@FechaGen'),
            fexml.xpath_from_root('/InformacionGeneral/@HoraGen'),
            fexml.xpath_from_root('/DevengadosTotal'),
            fexml.xpath_from_root('/DeduccionesTotal'),
            fexml.xpath_from_root('/ComprobanteTotal'),
            fexml.xpath_from_root('/Empleador/@NIT'),
            fexml.xpath_from_root('/Trabajador/@NumeroDocumento'),
            fexml.xpath_from_root('/InformacionGeneral/@TipoXML'),
            tuple([self.software_pin]),
            fexml.xpath_from_root('/InformacionGeneral/@Ambiente')
        ]
        campos = fexml.get_elements_text_or_attributes(xpaths)
        
        cune = "".join(campos)
        print(cune)
        h = hashlib.sha384()
        h.update(cune.encode('utf-8'))
        cune_hash = h.hexdigest()
    
        fragment.set_attributes(
            './InformacionGeneral',
            # NIE024
            CUNE = cune_hash
        )

class DianXMLExtensionSigner(fe.DianXMLExtensionSigner):

    def __init__(self, pkcs12_path, passphrase=None, mockpolicy=False):
        super().__init__(pkcs12_path, passphrase=passphrase, mockpolicy=mockpolicy)

    def _element_extension_content(self, fachoxml):
        return fachoxml.builder.xpath(fachoxml.root, './ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')


class DIANNominaXML:
    def __init__(self, tag_document):
        self.tag_document = tag_document
        self.fexml = fe.FeXML(tag_document, 'http://www.dian.gov.co/contratos/facturaelectronica/v1')

        # layout, la dian requiere que los elementos
        # esten ordenados segun el anexo tecnico
        self.fexml.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')
        self.fexml.placeholder_for('./Novedad', optional=True)
        self.fexml.placeholder_for('./Periodo')
        self.fexml.placeholder_for('./NumeroSecuenciaXML')
        self.fexml.placeholder_for('./LugarGeneracionXML')
        self.fexml.placeholder_for('./ProveedorXML')
        self.fexml.placeholder_for('./InformacionGeneral')
        self.fexml.placeholder_for('./Empleador')
        self.fexml.placeholder_for('./Trabajador')
        self.fexml.placeholder_for('./Pago')
        self.fexml.placeholder_for('./Devengados/Basico')
        self.fexml.placeholder_for('./Devengados/Transporte', optional=True)


        self.informacion_general_xml = self.fexml.fragment('./InformacionGeneral')
        self.numero_secuencia_xml = self.fexml.fragment('./NumeroSecuenciaXML')
        self.lugar_generacion_xml = self.fexml.fragment('./LugarGeneracionXML')
        self.proveedor_xml = self.fexml.fragment('./ProveedorXML')
        self.empleador = self.fexml.fragment('./Empleador')
        self.trabajador = self.fexml.fragment('./Trabajador')
        self.pago_xml = self.fexml.fragment('./Pago')
        self.devengados = self.fexml.fragment('./Devengados')
        self.deducciones = self.fexml.fragment('./Deducciones')

        self.informacion_general = None
        self.metadata = None

    def asignar_metadata(self, metadata):
        if not isinstance(metadata, Metadata):
            raise ValueError('se espera tipo Metadata')
        self.metadata = metadata
        self.metadata.apply(self.numero_secuencia_xml, self.lugar_generacion_xml, self.proveedor_xml)
        
    def asignar_informacion_general(self, general):
        if not isinstance(general, InformacionGeneral):
            raise ValueError('se espera tipo InformacionGeneral')
        self.informacion_general = general
        self.informacion_general.apply(self.informacion_general_xml)

    def asignar_pago(self, pago):
        if not isinstance(pago, Pago):
            raise ValueError('se espera tipo Pago')
        pago.apply(self.pago_xml)

    def asignar_empleador(self, empleador):
        if not isinstance(empleador, Empleador):
            raise ValueError('se espera tipo Empleador')
        empleador.apply(self.empleador)

    def asignar_trabajador(self, trabajador):
        if not isinstance(trabajador, Trabajador):
            raise ValueError('se espera tipo Trabajador')
        trabajador.apply(self.trabajador)
        
    def adicionar_devengado(self, devengado):
        if not isinstance(devengado, Devengado):
            raise ValueError('se espera tipo Devengado')

        devengado.apply(self.devengados)

    def adicionar_deduccion(self, deduccion):
        if not isinstance(deduccion, Deduccion):
            raise ValueError('se espera tipo Devengado')

        deduccion.apply(self.deducciones)

    def validate(self):
        """
        Valida requisitos segun anexo tecnico
        """
        errors = []

        def check_element(xpath, msg):
            if not self.fexml.exist_element(xpath):
                errors.append(DIANNominaIndividualError(msg))

        def check_attribute(xpath, key, msg):
            err = DIANNominaIndividualError(msg)
            elem = self.fexml.get_element(xpath)

            if elem is None:
                return errors.append(err)

            if elem.get(key, None) is None:
                return errors.append(err)

        check_attribute(
            self.fexml.xpath_from_root('/Periodo'),
            'FechaIngreso',
            'se requiere Periodo')

        check_element(
            self.fexml.xpath_from_root('/Pago'),
            'se requiere Pago'
        )

        check_element(
            self.fexml.xpath_from_root('/Devengados/Basico'),
            'se requiere DevengadoBasico'
        )
        
        check_element(
            self.fexml.xpath_from_root('/Deducciones/Salud'),
            'se requiere DeduccionSalud'
        )

        check_element(
            self.fexml.xpath_from_root('/Deducciones/FondoPension'),
            'se requiere DeduccionFondoPension'
        )

        return errors

    def toFachoXML(self):
        self._devengados_total()
        self._deducciones_total()
        self._comprobante_total()

        if self.informacion_general is not None:
            #TODO(bit4bit) acoplamiento temporal
            # es importante el orden de ejecucion

            self.informacion_general.post_apply(self.fexml, self.informacion_general_xml)

        if self.metadata is not None:
            self.metadata.post_apply(self.fexml, self.numero_secuencia_xml, self.lugar_generacion_xml, self.proveedor_xml)

        return self.fexml

    def _comprobante_total(self):
        devengados_total = self.fexml.get_element_text_or_attribute(self.fexml.xpath_from_root('/DevengadosTotal'), '0.0')
        deducciones_total = self.fexml.get_element_text_or_attribute(self.fexml.xpath_from_root('/DeduccionesTotal'), '0.0')

        comprobante_total = Amount(devengados_total) - Amount(deducciones_total)

        self.fexml.set_element(self.fexml.xpath_from_root('/ComprobanteTotal'), str(round(comprobante_total, 2)))

    def _deducciones_total(self):
        xpaths = [
            self.fexml.xpath_from_root('/Deducciones/Salud/@Deduccion'),
            self.fexml.xpath_from_root('/Deducciones/FondoPension/@Deduccion')
        ]
        deducciones = map(lambda valor: Amount(valor),
                          self._values_of_xpaths(xpaths))

        deducciones_total = Amount(0.0)
        
        for deduccion in deducciones:
            deducciones_total += deduccion

        self.fexml.set_element(f'/fe:{self.tag_document}/DeduccionesTotal', str(round(deducciones_total, 2)))

    def _devengados_total(self):
        xpaths = [
            self.fexml.xpath_from_root('/Devengados/Basico/@SueldoTrabajado'),
            self.fexml.xpath_from_root('/Devengados/Transporte/@AuxilioTransporte'),
            self.fexml.xpath_from_root('/Devengados/Transporte/@ViaticoManuAlojS'),
            self.fexml.xpath_from_root('/Devengados/Transporte/@ViaticoManuAlojNS')
        ]
        devengados = map(lambda valor: Amount(valor),
                         self._values_of_xpaths(xpaths))
        
        devengados_total = Amount(0.0)
        for devengado in devengados:
            devengados_total += devengado
            
        self.fexml.set_element(self.fexml.xpath_from_root('/DevengadosTotal'), str(round(devengados_total,2)))

    def _values_of_xpaths(self, xpaths):
        xpaths_values_of_values = map(lambda val: self.fexml.get_element_text_or_attribute(val, multiple=True), xpaths)
        xpaths_values = []
        # toda esta carreta para hacer un aplano de lista
        for xpath_values in xpaths_values_of_values:
            if xpath_values is None:
                continue

            for xpath_value in xpath_values:
                xpaths_values.append(xpath_value)

        return filter(lambda val: val is not None, xpaths_values)

class DIANNominaIndividual(DIANNominaXML):

    def __init__(self):
        super().__init__('NominaIndividual')

        
# TODO(bit4bit) confirmar que no tienen en comun con NominaIndividual
class DIANNominaIndividualDeAjuste(DIANNominaXML):

    def __init__(self):
        super().__init__('NominaIndividualDeAjuste')
