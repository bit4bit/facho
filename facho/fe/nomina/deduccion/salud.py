from dataclasses import dataclass

from ..amount import Amount
from .deduccion import Deduccion

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

