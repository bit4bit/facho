from dataclasses import dataclass

from ..amount import Amount
from .deduccion import Deduccion

@dataclass
class DeduccionFondoPension(Deduccion):
    porcentaje: Amount
    deduccion: Amount

    def apply(self, fragment):
        fragment.set_element('./FondoPension', None,
                             append_ = True,
                             # NIE164
                             Porcentaje = str(round(self.porcentaje, 2)),
                             #  NIE166
                             Deduccion = self.deduccion
                             )
