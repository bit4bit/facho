from dataclasses import dataclass
from typing import List

from ..amount import Amount
from .devengado import Devengado


@dataclass
class DevengadoHoraExtra:
    hora_inicio: str
    hora_fin: str
    cantidad: int
    porcentaje: Amount
    pago: Amount

    def apply(self, child_path, fragment):
        fragment.set_element(child_path, None,
                             append_=True,
                             # NIE074
                             HoraInicio=self.hora_inicio,
                             # NIE075
                             HoraFin=self.hora_fin,
                             # NIE076
                             Cantidad=self.cantidad,
                             # NIE077
                             Porcentaje=self.porcentaje,
                             # NIE078
                             Pago=str(round(self.pago, 2)))


@dataclass
class DevengadoHorasExtrasDiarias(Devengado):
    horas_extras: List[DevengadoHoraExtra]
    
    def apply(self, fragment):
        hora_extra_xml = fragment.fragment('./HEDs')
        for hora_extra in self.horas_extras:
            hora_extra.apply('./HED', hora_extra_xml)

@dataclass
class DevengadoHorasExtrasNocturnas(Devengado):
    horas_extras: List[DevengadoHoraExtra]
    
    def apply(self, fragment):
        hora_extra_xml = fragment.fragment('./HENs')
        for hora_extra in self.horas_extras:
            hora_extra.apply('./HEN', hora_extra_xml)


@dataclass
class DevengadoHorasRecargoNocturno(Devengado):
    horas_extras: List[DevengadoHoraExtra]
    
    def apply(self, fragment):
        hora_extra_xml = fragment.fragment('./HRNs')
        for hora_extra in self.horas_extras:
            hora_extra.apply('./HRN', hora_extra_xml)

@dataclass
class DevengadoHorasExtrasDiariasDominicalesYFestivos(Devengado):
    horas_extras: List[DevengadoHoraExtra]
    
    def apply(self, fragment):
        hora_extra_xml = fragment.fragment('./HEDDFs')
        for hora_extra in self.horas_extras:
            hora_extra.apply('./HEDDF', hora_extra_xml)

@dataclass
class DevengadoHorasRecargoDiariasDominicalesYFestivos(Devengado):
    horas_extras: List[DevengadoHoraExtra]
    
    def apply(self, fragment):
        hora_extra_xml = fragment.fragment('./HRDDFs')
        for hora_extra in self.horas_extras:
            hora_extra.apply('./HRDDF', hora_extra_xml)

@dataclass
class DevengadoHorasExtrasNocturnasDominicalesYFestivos(Devengado):
    horas_extras: List[DevengadoHoraExtra]
    
    def apply(self, fragment):
        hora_extra_xml = fragment.fragment('./HENDFs')
        for hora_extra in self.horas_extras:
            hora_extra.apply('./HENDF', hora_extra_xml)

@dataclass
class DevengadoHorasRecargoNocturnoDominicalesYFestivos(Devengado):
    horas_extras: List[DevengadoHoraExtra]
    
    def apply(self, fragment):
        hora_extra_xml = fragment.fragment('./HRNDFs')
        for hora_extra in self.horas_extras:
            hora_extra.apply('./HRNDF', hora_extra_xml)
