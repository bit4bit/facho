from .field import Field

class Function(Field):
    """
    Permite modificar el modelo cuando se intenta,
    obtener el valor de este campo.

    DEPRECATED usar Virtual
    """
    def __init__(self, field, getter=None, default=None):
        self.field = field
        self.getter = getter
        self.default = default

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None

        # si se indica `field` se adiciona
        # como campo del modelo, esto es
        # que se serializa a xml
        inst._set_field(self.name, self.field)

        if self.getter is not None:
            value = self._call(inst, self.getter, self.name, self.field)

            if value is not None:
                self.field.__set__(inst, value)

        return self.field

    def __set__(self, inst, value):
        inst._set_field(self.name, self.field)
        self._changed_field(inst, self.name, value)
        self.field.__set__(inst, value)
