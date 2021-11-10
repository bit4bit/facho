from dataclasses import dataclass

from facho.fe.data.dian import codelist

@dataclass
class TipoTrabajador:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.TipoTrabajador:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.TipoTrabajador[self.code]['name']
