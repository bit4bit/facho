#
# al crear objetos de valor
# se debe exportar en __all__

from .deduccion import *
from .salud import *
from .fondo_pension import *

__all__ = [
    'Deduccion',
    'DeduccionSalud',
    'DeduccionFondoPension'
]
