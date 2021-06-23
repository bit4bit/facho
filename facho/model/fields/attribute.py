from .field import Field

class Attribute(Field):
    def __init__(self, tag):
        self.tag = tag
  
    def __get__(self, inst, cls):
        if inst is None:
            return self

        assert self.name is not None
        (tag, value) =  inst._xml_attributes[self.name]
        return value

    def __set__(self, inst, value):
        assert self.name is not None
        inst._xml_attributes[self.name] = (self.tag, value)
