from dataclasses import dataclass

from ..amount import Amount
from .devengado import Devengado


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
