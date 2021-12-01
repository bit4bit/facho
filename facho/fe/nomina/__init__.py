#
# Para esta implementacion se usa BDD
# ver **test_nomina.py**.
#
# La idea en general es validar comportamiento desde el XML,
# creando las estructuras minimas necesaras.

from dataclasses import dataclass
from datetime import datetime
import hashlib
import typing

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

class Fecha:
    def __init__(self, fecha):
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            raise ValueError("fecha debe ser formato YYYY-MM-DD")
        self.value = fecha

    @classmethod
    def cast(cls, data, optional=False):
        if isinstance(data, str):
            return cls(data)
        elif isinstance(data, cls):
            return data
        elif data is None and optional:
            return None
        else:
            raise ValueError('no se logra hacer casting a Fecha')

    def __str__(self):
        return self.value

class FechaPago(Fecha):
    def apply(self, fragment):
        fragment.set_element('./FechaPago', self.value)

@dataclass
class NumeroSecuencia:
    consecutivo: int
    prefijo: str

    def apply(self, fragment):
        numero = f"{self.prefijo}{self.consecutivo}"
        fragment.set_attributes('./NumeroSecuenciaXML',
                                # NIE010
                                Prefijo=self.prefijo,
                                # NIE011
                                Consecutivo=self.consecutivo,
                                # NIE012
                                Numero = numero)

@dataclass
class Periodo:
    fecha_ingreso: typing.Union[str, Fecha]
    fecha_liquidacion_inicio: typing.Union[str, Fecha]
    fecha_liquidacion_fin: typing.Union[str, Fecha]
    fecha_generacion: typing.Union[str, Fecha]

    tiempo_laborado: int = 1
    fecha_retiro: typing.Union[str, Fecha] = None

    def __post_init__(self):
        self.fecha_ingreso = Fecha.cast(self.fecha_ingreso)
        self.fecha_liquidacion_inicio = Fecha.cast(self.fecha_liquidacion_inicio)
        self.fecha_liquidacion_fin = Fecha.cast(self.fecha_liquidacion_fin)
        self.fecha_retiro = Fecha.cast(self.fecha_retiro, optional=True)
        
    def apply(self, fragment):
        fragment.set_attributes('./Periodo',
                                #NIE002
                                FechaIngreso=self.fecha_ingreso,
                                #NIE003
                                FechaRetiro=self.fecha_retiro,
                                #NIE004
                                FechaLiquidacionInicio=self.fecha_liquidacion_inicio,
                                #NIE005
                                FechaLiquidacionFin=self.fecha_liquidacion_fin,
                                #NIE006
                                TiempoLaborado=self.tiempo_laborado,
                                #NIE008
                                FechaGen=self.fecha_generacion)
        
@dataclass
class Proveedor:
    razon_social: str
    nit: str
    dv: int
    software_id: str
    software_pin: str

    def apply(self, fragment):
        fragment.set_attributes('./ProveedorXML',
                                # NIE017
                                NIT=self.nit,
                                # NIE018
                                DV=self.dv,
                                # NIE019
                                SoftwareID=self.software_id,

                                SoftwareSC=None,
                                # NIE025
                                RazonSocial=self.razon_social
                                )

    def post_apply(self, fexml, scopexml, fragment):
        cune_xpath = scopexml.xpath_from_root('/InformacionGeneral')
        cune = fexml.get_element_attribute(cune_xpath, 'CUNE')
        
        ambiente = fexml.get_element_attribute(scopexml.xpath_from_root('/InformacionGeneral'), 'Ambiente')
        codigo_qr = f"https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={cune}"

        if InformacionGeneral.AMBIENTE_PRUEBAS.same(ambiente):
            codigo_qr = f"https://catalogo-vpfe-hab.dian.gov.co/document/searchqr?documentkey={cune}"
        elif ambiente is None:
            raise RuntimeError('fail to get InformacionGeneral/@Ambiente')
        
        scopexml.set_element('./CodigoQR', codigo_qr)

        # NIE020
        software_code = self._software_security_code(fexml, scopexml)
        fexml.set_attributes(scopexml.xpath_from_root('/ProveedorXML'), SoftwareSC=software_code)

    def _software_security_code(self, fexml, scopexml):
        

        # 8.2
        numero = fexml.get_element_attribute(scopexml.xpath_from_root('/NumeroSecuenciaXML'), 'Numero')
        if numero is None:
            raise RuntimeError('fallo obtener NumeroSequenciaXML/@Numero')
        
        id_software = self.software_id
        software_pin = self.software_pin

        code = "".join([id_software, software_pin, numero])

        fexml.set_attributes(scopexml.xpath_from_root('/ProveedorXML'), fachoSoftwareSC=code)
        h = hashlib.sha384()
        h.update(code.encode('utf-8'))
        return h.hexdigest()
    
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

    def post_apply(self, fexml, scopexml, numero_secuencia_xml, lugar_generacion_xml, proveedor_xml):
        self.proveedor.post_apply(fexml, scopexml, proveedor_xml)
        
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
    @dataclass
    class TIPO_AMBIENTE:
        valor: str

        @classmethod
        def same(cls, value):
            return cls.valor == str(value)

    # TABLA 5.1.1
    @dataclass
    class AMBIENTE_PRODUCCION(TIPO_AMBIENTE):
        valor: str = '1'

        def __str__(self):
            self.valor

    @dataclass
    class AMBIENTE_PRUEBAS(TIPO_AMBIENTE):
        valor: str = '2'

        def __str__(self):
            self.valor

    fecha_generacion: typing.Union[str, Fecha]
    hora_generacion: str
    periodo_nomina: PeriodoNomina
    tipo_moneda: TipoMoneda
    tipo_ambiente: TIPO_AMBIENTE
    software_pin: str

    def __post_init__(self):
        self.fecha_generacion = Fecha.cast(self.fecha_generacion)

    def apply(self, fragment, version):
        fragment.set_attributes('./InformacionGeneral',
                                # NIE022
                                Version = version,
                                # NIE023
                                Ambiente = self.tipo_ambiente.valor,
                                # NIE202
                                # TABLA 5.5.2
                                # TODO(bit4bit) solo NominaIndividual
                                TipoXML = '102',
                                # NIE024
                                CUNE = None,
                                # NIE025
                                EncripCUNE = 'CUNE-SHA384',
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

    def post_apply(self, fexml, scopexml, fragment):
        # generar cune
        # ver 8.1.1.1
        xpaths = [
            scopexml.xpath_from_root('/NumeroSecuenciaXML/@Numero'),
            scopexml.xpath_from_root('/InformacionGeneral/@FechaGen'),
            scopexml.xpath_from_root('/InformacionGeneral/@HoraGen'),
            scopexml.xpath_from_root('/DevengadosTotal'),
            scopexml.xpath_from_root('/DeduccionesTotal'),
            scopexml.xpath_from_root('/ComprobanteTotal'),
            scopexml.xpath_from_root('/Empleador/@NIT'),
            scopexml.xpath_from_root('/Trabajador/@NumeroDocumento'),
            scopexml.xpath_from_root('/InformacionGeneral/@TipoXML'),
            tuple([self.software_pin]),
            scopexml.xpath_from_root('/InformacionGeneral/@Ambiente')
        ]

        campos = fexml.get_elements_text_or_attributes(xpaths)

        cune = "".join(campos)

        h = hashlib.sha384()
        h.update(cune.encode('utf-8'))
        cune_hash = h.hexdigest()
    
        fragment.set_attributes(
            './InformacionGeneral',
            # NIE024
            CUNE = cune_hash,
            fachoCUNE = cune
        )

class DianXMLExtensionSigner(fe.DianXMLExtensionSigner):

    def __init__(self, pkcs12_path, passphrase=None, mockpolicy=False):
        super().__init__(pkcs12_path, passphrase=passphrase, mockpolicy=mockpolicy)

    def _element_extension_content(self, fachoxml):
        return fachoxml.builder.xpath(fachoxml.root, './ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')


class DIANNominaXML:
    def __init__(self, tag_document, xpath_ajuste=None,schemaLocation=None):
        self.informacion_general_version = None

        self.tag_document = tag_document
        self.fexml = fe.FeXML(tag_document, 'http://www.dian.gov.co/contratos/facturaelectronica/v1')

        if schemaLocation is not None:
            self.fexml.root.set("SchemaLocation", schemaLocation)

        # layout, la dian requiere que los elementos
        # esten ordenados segun el anexo tecnico
        self.fexml.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')
        self.fexml.placeholder_for('./TipoNota', optional=True)

        self.root_fragment = self.fexml
        if xpath_ajuste is not None:
            self.root_fragment = self.fexml.fragment(xpath_ajuste)
        self.root_fragment.placeholder_for('./ReemplazandoPredecesor', optional=True)
        self.root_fragment.placeholder_for('./EliminandoPredecesor', optional=True)
        self.root_fragment.placeholder_for('./Novedad', optional=True)
        self.root_fragment.placeholder_for('./Periodo')
        self.root_fragment.placeholder_for('./NumeroSecuenciaXML')
        self.root_fragment.placeholder_for('./LugarGeneracionXML')
        self.root_fragment.placeholder_for('./ProveedorXML')
        self.root_fragment.placeholder_for('./CodigoQR')
        self.root_fragment.placeholder_for('./InformacionGeneral')
        self.root_fragment.placeholder_for('./Empleador')
        self.root_fragment.placeholder_for('./Trabajador')
        self.root_fragment.placeholder_for('./Pago')
        self.root_fragment.placeholder_for('./FechasPagos')
        self.root_fragment.placeholder_for('./Devengados/Basico')
        self.root_fragment.placeholder_for('./Devengados/Transporte', optional=True)


        self.informacion_general_xml = self.root_fragment.fragment('./InformacionGeneral')
        self.periodo_xml = self.root_fragment.fragment('./Periodo')
        self.fecha_pagos_xml = self.root_fragment.fragment('./FechasPagos')
        self.numero_secuencia_xml = self.root_fragment.fragment('./NumeroSecuenciaXML')
        self.lugar_generacion_xml = self.root_fragment.fragment('./LugarGeneracionXML')
        self.proveedor_xml = self.root_fragment.fragment('./ProveedorXML')
        self.empleador = self.root_fragment.fragment('./Empleador')
        self.trabajador = self.root_fragment.fragment('./Trabajador')
        self.pago_xml = self.root_fragment.fragment('./Pago')
        self.devengados = self.root_fragment.fragment('./Devengados')
        self.deducciones = self.root_fragment.fragment('./Deducciones')

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
        self.informacion_general.apply(self.informacion_general_xml, self.informacion_general_version)

    def asignar_periodo(self, periodo):
        if not isinstance(periodo, Periodo):
            raise ValueError('se espera tipo Periodo')

        periodo.apply(self.periodo_xml)

    def asignar_pago(self, pago):
        if not isinstance(pago, Pago):
            raise ValueError('se espera tipo Pago')
        pago.apply(self.pago_xml)

    def asignar_fecha_pago(self, data):
        if isinstance(data, str):
            fecha = FechaPago(data)
        elif isinstance(data, FechaPago):
            fecha = data

        fecha.apply(self.fecha_pagos_xml)

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

    def informacion_general(self):
        xpath = self.root_fragment.xpath_from_root('/InformacionGeneral')
        return {
            'cune': self.fexml.get_element_attribute(cune_xpath, 'CUNE'),
            'fecha_generacion': self.fexml.get_element_attribute(xpath, 'FechaGen'),
            'numero': self.fexml.get_element_attribute(self.root_fragment('/NumeroSecuenciaXML', 'Numero'))
        }

    def toFachoXML(self):
        self._devengados_total()
        self._deducciones_total()
        self._comprobante_total()

        if self.informacion_general is not None:
            #TODO(bit4bit) acoplamiento temporal
            # es importante el orden de ejecucion

            self.informacion_general.post_apply(self.fexml, self.root_fragment, self.informacion_general_xml)

        if self.metadata is not None:
            self.metadata.post_apply(self.fexml, self.root_fragment, self.numero_secuencia_xml, self.lugar_generacion_xml, self.proveedor_xml)

        return self.fexml

    def _comprobante_total(self):
        devengados_total = self.root_fragment.get_element_text_or_attribute('./DevengadosTotal', '0.0')
        deducciones_total = self.root_fragment.get_element_text_or_attribute('./DeduccionesTotal', '0.0')

        comprobante_total = Amount(devengados_total) - Amount(deducciones_total)

        self.root_fragment.set_element('./ComprobanteTotal', str(round(comprobante_total, 2)))

    def _deducciones_total(self):
        xpaths = [
            self.root_fragment.xpath_from_root('/Deducciones/Salud/@Deduccion'),
            self.root_fragment.xpath_from_root('/Deducciones/FondoPension/@Deduccion')
        ]
        deducciones = map(lambda valor: Amount(valor),
                          self._values_of_xpaths(xpaths))

        deducciones_total = Amount(0.0)
        
        for deduccion in deducciones:
            deducciones_total += deduccion

        self.root_fragment.set_element('./DeduccionesTotal', str(round(deducciones_total, 2)))

    def _devengados_total(self):
        xpaths = [
            self.root_fragment.xpath_from_root('/Devengados/Basico/@SueldoTrabajado'),
            self.root_fragment.xpath_from_root('/Devengados/Transporte/@AuxilioTransporte'),
            self.root_fragment.xpath_from_root('/Devengados/Transporte/@ViaticoManuAlojS'),
            self.root_fragment.xpath_from_root('/Devengados/Transporte/@ViaticoManuAlojNS')
        ]
        devengados = map(lambda valor: Amount(valor),
                         self._values_of_xpaths(xpaths))
        
        devengados_total = Amount(0.0)
        for devengado in devengados:
            devengados_total += devengado
            
        self.root_fragment.set_element('./DevengadosTotal', str(round(devengados_total,2)))

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
        schema = "dian:gov:co:facturaelectronica:NominaIndividual NominaIndividualElectronicaXSD.xsd"

        super().__init__('NominaIndividual', schemaLocation=schema)
        self.informacion_general_version = 'V1.0: Documento Soporte de Pago de Nómina Electrónica'

# TODO(bit4bit) confirmar que no tienen en comun con NominaIndividual
class DIANNominaIndividualDeAjuste(DIANNominaXML):

    class Reemplazar(DIANNominaXML):
        @dataclass
        class Predecesor:
            numero: str
            cune: str
            fecha_generacion: str

            def apply(self, fragment):
                fragment.set_element('./Reemplazar/ReemplazandoPredecesor', None,
                                     # NIAE090
                                     NumeroPred = self.numero,
                                     # NIAE191
                                     CUNEPred = self.cune,
                                     # NIAE192
                                     FechaGenPred = self.fecha_generacion
                                     )

        def __init__(self):
            super().__init__('NominaIndividualDeAjuste', './Reemplazar')
            # NIAE214
            self.root_fragment.set_element('./TipoNota', '1')

        def asignar_predecesor(self, predecesor):
            if not isinstance(predecesor, self.Predecesor):
                raise ValueError("se espera tipo Predecesor")
            predecesor.apply(self.fexml)

        
    class Eliminar(DIANNominaXML):
        
        @dataclass
        class Predecesor:
            numero: str
            cune: str
            fecha_generacion: str

            def apply(self, fragment):
                fragment.set_element('./Eliminar/EliminandoPredecesor', None,
                                     # NIAE090
                                     NumeroPred = self.numero,
                                     # NIAE191
                                     CUNEPred = self.cune,
                                     # NIAE192
                                     FechaGenPred = self.fecha_generacion
                                     )

        def __init__(self):
            super().__init__('NominaIndividualDeAjuste', './Eliminar')

            self.root_fragment.set_element('./TipoNota', '2')
            self.informacion_general_version = "V1.0: Nota de Ajuste de Documento Soporte de Pago de Nómina Electrónica"

        def asignar_predecesor(self, predecesor):
            if not isinstance(predecesor, self.Predecesor):
                raise ValueError("se espera tipo Eliminar.Predecesor")
            predecesor.apply(self.fexml)
            
    def __init__(self):
        super().__init__('NominaIndividualDeAjuste')

