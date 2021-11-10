from dataclasses import dataclass

from facho.fe.data.dian import codelist

@dataclass
class MetodoPago:
    code: str
    name: str = ''

    def __post_init__(self):
        if self.code not in codelist.MediosPago:
            raise ValueError("code [%s] not found" % (self.code))
        self.name = codelist.MediosPago[self.code]['name']

