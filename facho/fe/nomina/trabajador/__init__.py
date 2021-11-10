from dataclasses import dataclass

from ..amount import Amount

from .tipo_contrato import *
from .tipo_documento import *
from .lugar_trabajo import *
from .tipo_trabajador import *
from .sub_tipo_trabajador import *



@dataclass
class Trabajador:
    tipo_contrato: TipoContrato
    tipo_documento: TipoDocumento
    numero_documento: str

    primer_apellido: str
    segundo_apellido: str
    primer_nombre: str

    lugar_trabajo: LugarTrabajo
    alto_riesgo: bool
    salario_integral: bool
    sueldo: Amount

    tipo: TipoTrabajador

    codigo_trabajador: str = None
    otros_nombres: str = None
    sub_tipo: SubTipoTrabajador = SubTipoTrabajador(code='00')

    def apply(self, fragment):
        fragment.set_attributes('./Trabajador',
                                # NIE041
                                TipoTrabajador = self.tipo.code,
                                # NIE042
                                SubTipoTrabajador = self.sub_tipo.code,
                                # NIE043
                                AltoRiesgoPension = str(self.alto_riesgo).lower(),
                                # NIE044
                                TipoDocumento = self.tipo_documento.code,
                                # NIE045
                                NumeroDocumento = self.numero_documento,
                                # NIE046
                                PrimerApellido = self.primer_apellido,
                                # NIE047
                                SegundoApellido = self.segundo_apellido,
                                # NIE048
                                PrimerNombre = self.primer_nombre,
                                # NIE049
                                OtrosNombres = self.otros_nombres,
                                # NIE050
                                LugarTrabajoPais = self.lugar_trabajo.pais.code,

                                # NIE051
                                LugarTrabajoDepartamentoEstadoEstado = self.lugar_trabajo.departamento.code,

                                # NIE052
                                LugarTrabajoMunicipioCiudad = self.lugar_trabajo.municipio.code,

                                # NIE053
                                LugarTrabajoDireccion = self.lugar_trabajo.direccion,
                                # NIE056
                                SalarioIntegral = str(self.salario_integral).lower(),
                                # NIE061
                                TipoContrato = self.tipo_contrato.code,
                                # NIE062
                                Sueldo = str(self.sueldo),
                                # NIE063
                                CodigoTrabajador = self.codigo_trabajador
                                )
