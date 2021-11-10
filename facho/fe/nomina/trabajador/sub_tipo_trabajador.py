from dataclasses import dataclass

from facho.fe.data.dian import codelist

@dataclass
class SubTipoTrabajador:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.SubTipoTrabajador:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.SubTipoTrabajador[self.code]['name']
