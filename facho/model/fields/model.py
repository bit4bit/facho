from .field import Field

class Model(Field):
    def __init__(self, model, namespace=None):
        self.model = model
        self.namespace = namespace

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
            self._set_namespace(obj, self.namespace, inst.__namespace__)
            inst._fields[self.name] = obj
            return obj
            
