from .field import Field

class Model(Field):
    def __init__(self, model, name=None, namespace=None):
        self.model = model
        self.namespace = namespace
        self.field_name = name

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None
        return self._create_model(inst, name=self.field_name)

    def __set__(self, inst, value):
        obj = self._create_model(inst, name=self.field_name)
        obj._set_content(value)            
