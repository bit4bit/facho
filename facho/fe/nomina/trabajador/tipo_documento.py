from dataclasses import dataclass

from facho.fe.data.dian import codelist

@dataclass
class TipoDocumento:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.TipoIdFiscal:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.TipoIdFiscal[self.code]['name']
