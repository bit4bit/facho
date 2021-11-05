from .. import fe
from .. import form

from dataclasses import dataclass

class Amount(form.Amount):
    pass


class Devengado:
    pass

@dataclass
class DevengadoBasico(Devengado):
    dias_trabajados: int
    sueldo_trabajado: Amount

    def apply(self, fragment):
        fragment.find_or_create_element('./Basico')
        
        fragment.set_attributes('/Basico',
                                # NIE069
                                DiasTrabajados = str(self.dias_trabajados),
                                # NIE070
                                SueldoTrabajado = str(self.sueldo_trabajado)
                                )

@dataclass
class DevengadoTransporte(Devengado):
    auxilio_transporte: Amount = None
    viatico_manutencion: Amount = None
    viatico_manutencion_no_salarial: Amount = None

    def apply(self, fragment):
        fragment.set_element('./Transporte', None,
                             append_ = True,
                             # NIE071
                             AuxilioTransporte = self.auxilio_transporte,
                             # NIE072
                             ViaticoManuAlojS = self.viatico_manutencion,
                             # NIE073
                             ViaticoManuAlojNS = self.viatico_manutencion_no_salarial
                             )

class Deduccion:
    pass

@dataclass
class DeduccionSalud(Deduccion):
    porcentaje: Amount
    deduccion: Amount

    def apply(self, fragment):
        fragment.set_element('./Salud', None,
                             append_ = True,
                             # NIE161
                             Porcentaje = self.porcentaje,
                             #  NIE163
                             Deduccion = self.deduccion
                             )

@dataclass
class DeduccionFondoPension(Deduccion):
    porcentaje: Amount
    deduccion: Amount

    def apply(self, fragment):
        fragment.set_element('./FondoPension', None,
                             append_ = True,
                             # NIE164
                             Porcentaje = self.porcentaje,
                             #  NIE166
                             Deduccion = self.deduccion
                             )

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

        def add_error(xpath, msg):
            if not self.fexml.exist_element(xpath):
                errors.append(DIANNominaIndividualError(msg))

        add_error('/fe:NominaIndividual/Devengados/Basico',
                  'se requiere DevengadoBasico')

        add_error('/fe:NominaIndividual/Deducciones/Salud',
                  'se requiere DeduccionSalud')

        add_error('/fe:NominaIndividual/Deducciones/FondoPension',
                  'se requiere DeduccionFondoPension')

        return errors

    def toFachoXML(self):
        return self.fexml
