from .field import Field

# Un campo virtual
# no participa del renderizado
# pero puede interactura con este
class Virtual(Field):
    def __init__(self,
                 setter=None,
                 getter='bob',
                 default=None,
                 update_internal=False):
        self.default = default
        self.setter = setter
        self.getter = getter
        self.values = {}
        self.update_internal = update_internal
        self.virtual = True

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None

        value = self.default
        try:
            value = self.values[inst]
        except KeyError:
            pass

        try:
            self.values[inst] = getattr(inst, self.getter)(self.name, value)
        except AttributeError:
            self.values[inst] = value

        return self.values[inst]
    
    def __set__(self, inst, value):
        if self.update_internal:
            inst._value = value

        if self.setter is None:
            self.values[inst] = value
        else:
            self.values[inst] = self._call(inst, self.setter, self.name, value)
        self._changed_field(inst, self.name, value)        
