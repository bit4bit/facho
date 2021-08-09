from .field import Field
from collections import defaultdict

class Many2One(Field):
    """
    Many2One describe una relacion pertenece a.
    """

    def __init__(self, model, name=None, setter=None, namespace=None, default=None, virtual=False, create=False):
        """
        :param model: nombre del modelo destino
        :param name: nombre del elemento xml
        :param setter: nombre de methodo usado cuando se asigna usa como asignacion ejemplo model.relation = 3
        :param namespace: sufijo del namespace al que pertenece el elemento
        :param default: el valor o contenido por defecto
        :param virtual: se crea la relacion por no se ve reflejada en el xml final
        :param create: fuerza la creacion del elemento en el xml, ya que los elementos no son creados sino tienen contenido
        """
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


