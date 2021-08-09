from .field import Field

# Un campo virtual
# no participa del renderizado
# pero puede interactura con este
class Virtual(Field):
    """
    Virtual es un campo que no es renderizado en el xml final
    """
    def __init__(self,
                 setter=None,
                 getter='',
                 default=None,
                 update_internal=False):
        """
        :param setter: nombre de methodo usado cuando se asigna usa como asignacion ejemplo model.relation = 3
        :param getter: nombre del metodo usando cuando se obtiene, ejemplo: valor = mode.relation
        :param default: valor por defecto
        :param update_internal: indica que cuando se asigne algun valor este se almacena localmente
        """
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
