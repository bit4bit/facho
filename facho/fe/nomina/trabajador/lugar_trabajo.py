from dataclasses import dataclass

from . import *
from ..pais import Pais
from ..departamento import Departamento
from ..municipio import Municipio

@dataclass
class LugarTrabajo:
    pais: Pais
    departamento: Departamento
    municipio: Municipio
    direccion: str
