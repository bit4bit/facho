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

from .amount import Amount
from .exception import *

@dataclass
class NumeroSecuencia:
    numero: str

    def apply(self, fragment):
        fragment.set_attributes('./NumeroSecuenciaXML',
                                Numero = self.numero)
        
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

class Pais(form.Country):
    pass

class Departamento(form.CountrySubentity):
    pass

class Municipio(form.City):
    pass

@dataclass
class Empleador:
    nit: str
    dv: str
    pais: Pais
    departamento: Departamento
    municipio: Municipio
    direccion: str

    def apply(self, fragment):
        fragment.set_attributes('./Empleador',
                                # NIE033
                                NIT = self.nit,
                                # NIE034
                                DV = self.dv,
                                # NIE035
                                Pais = self.pais.code,
                                # NIE036
                                DepartamentoEstado = self.departamento.code,
                                # NIE037
                                MunicipioCiudad = self.municipio.code,
                                # NIE038
                                Direccion = self.direccion
                                )


@dataclass
class TipoTrabajador:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.TipoTrabajador:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.TipoTrabajador[self.code]['name']

@dataclass
class SubTipoTrabajador:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.SubTipoTrabajador:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.SubTipoTrabajador[self.code]['name']

@dataclass
class TipoDocumento:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.TipoIdFiscal:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.TipoIdFiscal[self.code]['name']

@dataclass
class TipoContrato:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.TipoContrato:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.TipoContrato[self.code]['name']

@dataclass
class LugarTrabajo:
    pais: Pais
    departamento: Departamento
    municipio: Municipio
    direccion: str

@dataclass
class Trabajador:
    tipo_contrato: TipoContrato
    tipo_documento: TipoDocumento
    numero_documento: str

    primer_apellido: str
    segundo_apellido: str
    primer_nombre: str

    lugar_trabajo: LugarTrabajo
    alto_riesgo: bool
    salario_integral: bool
    sueldo: Amount

    tipo: TipoTrabajador

    codigo_trabajador: str = None
    otros_nombres: str = None
    sub_tipo: SubTipoTrabajador = SubTipoTrabajador(code='00')

    def apply(self, fragment):
        fragment.set_attributes('./Trabajador',
                                # NIE041
                                TipoTrabajador = self.tipo.code,
                                # NIE042
                                SubTipoTrabajador = self.sub_tipo.code,
                                # NIE043
                                AltoRiesgoPension = str(self.alto_riesgo).lower(),
                                # NIE044
                                TipoDocumento = self.tipo_documento.code,
                                # NIE045
                                NumeroDocumento = self.numero_documento,
                                # NIE046
                                PrimerApellido = self.primer_apellido,
                                # NIE047
                                SegundoApellido = self.segundo_apellido,
                                # NIE048
                                PrimerNombre = self.primer_nombre,
                                # NIE049
                                OtrosNombres = self.otros_nombres,
                                # NIE050
                                LugarTrabajoPais = self.lugar_trabajo.pais.code,

                                # NIE051
                                LugarTrabajoDepartamentoEstadoEstado = self.lugar_trabajo.departamento.code,

                                # NIE052
                                LugarTrabajoMunicipioCiudad = self.lugar_trabajo.municipio.code,

                                # NIE053
                                LugarTrabajoDireccion = self.lugar_trabajo.direccion,
                                # NIE056
                                SalarioIntegral = str(self.salario_integral).lower(),
                                # NIE061
                                TipoContrato = self.tipo_contrato.code,
                                # NIE062
                                Sueldo = str(self.sueldo),
                                # NIE063
                                CodigoTrabajador = self.codigo_trabajador
                                )



@dataclass
class FormaPago:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.FormasPago:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.FormasPago[self.code]['name']

@dataclass
class MetodoPago:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.MediosPago:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.MediosPago[self.code]['name']

@dataclass
class Pago:
    forma: FormaPago
    metodo: MetodoPago

    def apply(self, fragment):
        fragment.set_attributes('./Pago',
                                # NIE064
                                Forma = self.forma.code,
                                # NIE065
                                Metodo = self.metodo.code)
                                
class DIANNominaXML:
    def __init__(self, tag_document):
        self.tag_document = tag_document
        self.fexml = fe.FeXML(tag_document, 'http://www.dian.gov.co/contratos/facturaelectronica/v1')

        # layout, la dian requiere que los elementos
        # esten ordenados segun el anexo tecnico
        self.fexml.placeholder_for('./NumeroSecuenciaXML')
        self.fexml.placeholder_for('./InformacionGeneral')
        self.fexml.placeholder_for('./Empleador')
        self.fexml.placeholder_for('./Trabajador')
        self.fexml.placeholder_for('./Pago')
        self.fexml.placeholder_for('./Devengados/Basico')
        self.fexml.placeholder_for('./Devengados/Transporte', optional=True)


        self.informacion_general_xml = self.fexml.fragment('./InformacionGeneral')
        self.numero_secuencia_xml = self.fexml.fragment('./NumeroSecuenciaXML')
        self.empleador = self.fexml.fragment('./Empleador')
        self.trabajador = self.fexml.fragment('./Trabajador')
        self.pago_xml = self.fexml.fragment('./Pago')
        self.devengados = self.fexml.fragment('./Devengados')
        self.deducciones = self.fexml.fragment('./Deducciones')

        self.informacion_general = None

    def asignar_numero_secuencia(self, secuencia):
        if not isinstance(secuencia, NumeroSecuencia):
            raise ValueError('se espera tipo NumeroSecuencia')
        secuencia.apply(self.numero_secuencia_xml)

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
