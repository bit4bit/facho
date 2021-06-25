from .field import Field

class Attribute(Field):
    def __init__(self, name, default=None):
        self.attribute = name
        self.value = default
        self.default = default

    def __get__(self, inst, cls):
        if inst is None:
            return self

        assert self.name is not None
        return self.value

    def __set__(self, inst, value):
        assert self.name is not None
        self.value = value
        inst._set_attribute(self.name, self.attribute, value)
