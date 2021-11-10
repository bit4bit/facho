from dataclasses import dataclass

from .forma_pago import FormaPago
from .metodo_pago import MetodoPago

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
