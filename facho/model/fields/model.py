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
        return self._create_model(inst)

    def __set__(self, inst, value):
        obj = self._create_model(inst)
        obj._text = str(value)

    def _create_model(self, inst):
        try:
            return inst._fields[self.name]
        except KeyError:
            obj = self.model()
            if self.field_name is not None:
                obj.__name__ = self.field_name
            self._set_namespace(obj, self.namespace, inst.__namespace__)
            inst._fields[self.name] = obj
            return obj
            
