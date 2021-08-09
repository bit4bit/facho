from .field import Field

class Attribute(Field):
    """
    Attribute es un atributo del elemento actual.
    """
    
    def __init__(self, name, default=None):
        """
        :param name: nombre del atribute
        :param default: valor por defecto del attributo
        """
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
        
        self._changed_field(inst, self.name, value)
        inst._set_attribute(self.name, self.attribute, value)
