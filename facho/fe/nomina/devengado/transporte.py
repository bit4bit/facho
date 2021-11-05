from dataclasses import dataclass

from ..amount import Amount
from .devengado import Devengado

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
