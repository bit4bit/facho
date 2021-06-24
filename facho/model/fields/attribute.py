from .field import Field

class Attribute(Field):
    def __init__(self, tag, default=None):
        self.tag = tag
        self.value = default

    def __get__(self, inst, cls):
        if inst is None:
            return self

        assert self.name is not None
        return self.value

    def __set__(self, inst, value):
        assert self.name is not None
        self.value = value
        inst._xml_attributes[self.name] = (self.tag, value)
