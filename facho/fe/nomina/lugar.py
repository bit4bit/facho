from dataclasses import dataclass

from .pais import Pais
from .departamento import Departamento
from .municipio import Municipio
from facho.fe.data.dian import codelist

@dataclass
class Lugar:
    pais: Pais
    departamento: Departamento
    municipio: Municipio
    idioma: str = 'es'

    def __post_init__(self):
        if self.idioma not in codelist.IdiomaISO6391:
            raise ValueError("idioma [%s] not found" % (self.code))
        codelist.IdiomaISO6391[self.idioma]['iso-639-1']

    def apply(self, fragment, root):
        fragment.set_attributes(root,
                                Pais=self.pais.code,
                                DepartamentoEstado=self.departamento.code,
                                MunicipioCiudad=self.municipio.code)
