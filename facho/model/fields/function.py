from .field import Field
from .model import Model

class Function(Field):
    def __init__(self, getter, setter=None, field=None):
        self.field = field
        self.getter = getter
        self.setter = setter

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None

        if self.field is None:
            return self._call(inst, self.getter, self.name)
        else:
            obj = Model(self.field)
            return self._call(inst, self.getter, self.name, obj)

    def __set__(self, inst, value):
        if self.setter is None:
            return super().__set__(self.name, value)
        self._call(inst, self.setter, self.name, value)
