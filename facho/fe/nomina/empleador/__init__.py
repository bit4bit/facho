from dataclasses import dataclass

from ..pais import Pais
from ..departamento import Departamento
from ..municipio import Municipio

@dataclass
class Empleador:
    nit: str
    dv: str
    pais: Pais
    departamento: Departamento
    municipio: Municipio
    direccion: str

    def apply(self, fragment):
        fragment.set_attributes('./Empleador',
                                # NIE033
                                NIT = self.nit,
                                # NIE034
                                DV = self.dv,
                                # NIE035
                                Pais = self.pais.code,
                                # NIE036
                                DepartamentoEstado = self.departamento.code,
                                # NIE037
                                MunicipioCiudad = self.municipio.code,
                                # NIE038
                                Direccion = self.direccion
                                )


