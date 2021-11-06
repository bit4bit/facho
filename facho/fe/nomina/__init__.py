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
        xpaths = [
            '/fe:NominaIndividual/NumeroSecuenciaXML/@Numero',
            '/fe:NominaIndividual/InformacionGeneral/@FechaGen',
            '/fe:NominaIndividual/InformacionGeneral/@HoraGen',
            '/fe:NominaIndividual/DevengadosTotal',
            '/fe:NominaIndividual/DeduccionesTotal',
            '/fe:NominaIndividual/ComprobanteTotal',
            '/fe:NominaIndividual/Empleador/@NIT',
            '/fe:NominaIndividual/Trabajador/@NumeroDocumento',
            '/fe:NominaIndividual/InformacionGeneral/@TipoXML',
            tuple([self.software_pin]),
            '/fe:NominaIndividual/InformacionGeneral/@Ambiente'
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

@dataclass
class Empleador:
    nit: str

    def apply(self, fragment):
        fragment.set_attributes('./Empleador',
                                NIT = self.nit)
    
@dataclass
class Trabajador:
    numero_documento: str

    def apply(self, fragment):
        fragment.set_attributes('./Trabajador',
                                NumeroDocumento = self.numero_documento)

class DIANNominaIndividual:
    def __init__(self):
        self.fexml = fe.FeXML('NominaIndividual', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')

        # layout, la dian requiere que los elementos
        # esten ordenados segun el anexo tecnico
        self.fexml.placeholder_for('./NumeroSecuenciaXML')
        self.fexml.placeholder_for('./InformacionGeneral')
        self.fexml.placeholder_for('./Empleador')
        self.fexml.placeholder_for('./Trabajador')
        self.fexml.placeholder_for('./Devengados/Basico')
        self.fexml.placeholder_for('./Devengados/Transporte', optional=True)


        self.informacion_general_xml = self.fexml.fragment('./InformacionGeneral')
        self.numero_secuencia_xml = self.fexml.fragment('./NumeroSecuenciaXML')
        self.empleador = self.fexml.fragment('./Empleador')
        self.trabajador = self.fexml.fragment('./Trabajador')
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

        check_attribute('/fe:NominaIndividual/Periodo', 'FechaIngreso', 'se requiere Periodo')
        
        check_element(
            '/fe:NominaIndividual/Devengados/Basico',
            'se requiere DevengadoBasico'
        )
        
        check_element(
            '/fe:NominaIndividual/Deducciones/Salud',
            'se requiere DeduccionSalud'
        )

        check_element(
            '/fe:NominaIndividual/Deducciones/FondoPension',
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
        devengados_total = self.fexml.get_element_text_or_attribute('/fe:NominaIndividual/DevengadosTotal', '0.0')
        deducciones_total = self.fexml.get_element_text_or_attribute('/fe:NominaIndividual/DeduccionesTotal', '0.0')

        comprobante_total = Amount(devengados_total) - Amount(deducciones_total)

        self.fexml.set_element('/fe:NominaIndividual/ComprobanteTotal', str(round(comprobante_total, 2)))

    def _deducciones_total(self):
        xpaths = [
            '/fe:NominaIndividual/Deducciones/Salud/@Deduccion',
            '/fe:NominaIndividual/Deducciones/FondoPension/@Deduccion'
        ]
        deducciones = map(lambda valor: Amount(valor),
                          self._values_of_xpaths(xpaths))

        deducciones_total = Amount(0.0)
        
        for deduccion in deducciones:
            deducciones_total += deduccion

        self.fexml.set_element('/fe:NominaIndividual/DeduccionesTotal', str(round(deducciones_total, 2)))

    def _devengados_total(self):
        xpaths = [
            '/fe:NominaIndividual/Devengados/Basico/@SueldoTrabajado',
            '/fe:NominaIndividual/Devengados/Transporte/@AuxilioTransporte',
            '/fe:NominaIndividual/Devengados/Transporte/@ViaticoManuAlojS',
            '/fe:NominaIndividual/Devengados/Transporte/@ViaticoManuAlojNS'
        ]
        devengados = map(lambda valor: Amount(valor),
                         self._values_of_xpaths(xpaths))
        
        devengados_total = Amount(0.0)
        for devengado in devengados:
            devengados_total += devengado
            
        self.fexml.set_element('/fe:NominaIndividual/DevengadosTotal', str(round(devengados_total,2)))

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
