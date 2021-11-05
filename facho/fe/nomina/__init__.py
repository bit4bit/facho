#
# Para esta implementacion se usa BDD
# ver **test_nomina.py**.
#
# La idea en general es validar comportamiento desde el XML,
# creando las estructuras minimas necesaras.

from dataclasses import dataclass

from .. import fe
from .. import form

from .devengado import *
from .deduccion import *

from .amount import Amount


class DIANNominaIndividualError(Exception):
    pass

class DIANNominaIndividual:
    def __init__(self):
        self.fexml = fe.FeXML('NominaIndividual', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')

        # layout, la dian requiere que los elementos
        # esten ordenados segun el anexo tecnico
        self.fexml.placeholder_for('./Devengados/Basico')
        self.fexml.placeholder_for('./Devengados/Transporte', optional=True)

        self.devengados = self.fexml.fragment('./Devengados')
        self.deducciones = self.fexml.fragment('./Deducciones')

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
        return self.fexml
