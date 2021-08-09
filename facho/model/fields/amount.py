from .field import Field
from collections import defaultdict
import facho.fe.form as form

class Amount(Field):
    """
    Amount representa un campo moneda usando form.Amount
    """

    def __init__(self, name=None, default=None, precision=6):
        self.field_name = name
        self.values = {}
        self.default = default
        self.precision = precision
        
    def __get__(self, model, cls):
        if model is None:
            return self
        assert self.name is not None
 
        self.__init_value(model)
        model._set_field(self.name, self)
        return self.values[model]

    def __set__(self, model, value):
        assert self.name is not None
        self.__init_value(model)
        model._set_field(self.name, self)
        self.values[model] = form.Amount(value, precision=self.precision)

        self._changed_field(model, self.name, value)

    def __init_value(self, model):
        if model not in self.values:
            self.values[model] = form.Amount(self.default or 0)
