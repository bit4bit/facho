from .field import Field
from collections import defaultdict

class Many2One(Field):
    def __init__(self, model, name=None, setter=None, namespace=None, default=None, virtual=False, create=False):
        self.model = model
        self.setter = setter
        self.namespace = namespace
        self.field_name = name
        self.default = default
        self.virtual = virtual
        self.relations = defaultdict(dict)
        self.create = create

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None

        if self.name in self.relations:
            value = self.relations[inst][self.name]
        else:
            value = self._create_model(inst, name=self.field_name)
        self.relations[inst][self.name] = value

        # se puede obtener directamente un valor indicado por el modelo
        if hasattr(value, '__default_get__'):
            return value.__default_get__(self.name, value)
        elif hasattr(inst, '__default_get__'):
            return inst.__default_get__(self.name, value)
        else:
            return value
        
    def __set__(self, inst, value):
        assert self.name is not None
        inst_model = self._create_model(inst, name=self.field_name, model=self.model)
        self.relations[inst][self.name] = inst_model

        # si hay setter manual se ejecuta
        # de lo contrario se asigna como texto del elemento
        setter = getattr(inst, self.setter or '', None)
        if callable(setter):
            setter(inst_model, value)
        else:
            inst_model._set_content(value)
            
        self._changed_field(inst, self.name, value)


