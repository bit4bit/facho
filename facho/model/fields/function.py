from .field import Field
from .model import Model

class Function(Field):
    def __init__(self, field, getter=None):
        self.field = field
        self.getter = getter

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None

        # si se indica `field` se adiciona
        # como campo del modelo, esto es
        # que se serializa a xml
        self.field.name = self.name
        inst._fields[self.name] = self.field

        if self.getter is not None:
            value = self._call(inst, self.getter, self.name, self.field)

            if value is not None:
                self.field.__set__(inst, value)

        return self.field
