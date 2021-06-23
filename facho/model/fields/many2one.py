from .field import Field

class Many2One(Field):
    def __init__(self, model, setter=None, namespace=None):
        self.model = model
        self.setter = setter
        self.namespace = namespace

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None
        return inst._fields[self.name]
        
    def __set__(self, inst, value):
        assert self.name is not None
        class_model = self.model
        inst_model = class_model()

        self._set_namespace(inst_model, self.namespace,  inst.__namespace__)
        inst._fields[self.name] = inst_model

        # si hay setter manual se ejecuta
        # de lo contrario se asigna como texto del elemento
        setter = getattr(inst, self.setter or '', None)
        if callable(setter):
            setter(inst_model, value)
        else:
            inst_model._text = str(value)



