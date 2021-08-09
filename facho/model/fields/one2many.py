from .field import Field
from collections import defaultdict

# TODO(bit4bit) lograr que isinstance se aplique
# al objeto envuelto
class _RelationProxy():
    def __init__(self, obj, inst, attribute):
        self.__dict__['_obj'] = obj
        self.__dict__['_inst'] = inst
        self.__dict__['_attribute'] = attribute

    def __getattr__(self, name):
        if (name in self.__dict__):
            return self.__dict__[name]

        rel = getattr(self.__dict__['_obj'], name)
        if hasattr(rel, '__default_get__'):
            return rel.__default_get__(name, rel)

        return rel

    def __setattr__(self, attr, value):
        # TODO(bit4bit) hacemos proxy al sistema de notificacion de cambios
        # algo burdo, se usa __dict__ para saltarnos el __getattr__ y evitar un fallo por recursion
        rel = getattr(self.__dict__['_obj'], attr)
        if hasattr(rel, '__default_set__'):
            response = setattr(self._obj, attr, rel.__default_set__(value))
        else:
            response = setattr(self._obj, attr, value)

        for fun in self.__dict__['_inst']._on_change_fields[self.__dict__['_attribute']]:
            fun(self.__dict__['_inst'], self.__dict__['_attribute'], value)
        return response

class _Relation():
    def __init__(self, creator, inst, attribute):
        self.creator = creator
        self.inst = inst
        self.attribute = attribute
        self.relations = []

    def create(self):
        n_relations = len(self.relations)
        attribute = '%s_%d' % (self.attribute, n_relations)
        relation = self.creator(attribute)
        proxy = _RelationProxy(relation, self.inst, self.attribute)

        self.relations.append(relation)
        return proxy

    def __len__(self):
        return len(self.relations)

    def __iter__(self):
        for relation in self.relations:
            yield relation

class One2Many(Field):
    """
    One2Many describe una relacion tiene muchos.
    """

    def __init__(self, model, name=None, namespace=None, default=None):
        """
        :param model: nombre del modelo destino
        :param name: nombre del elemento xml cuando se crea hijo
        :param namespace: sufijo del namespace al que pertenece el elemento
        :param default: el valor o contenido por defecto
        """
        self.model = model
        self.field_name = name
        self.namespace = namespace
        self.default = default
        self.relation = {}
        
    def __get__(self, inst, cls):
        assert self.name is not None

        def creator(attribute):
            return self._create_model(inst, name=self.field_name, model=self.model, attribute=attribute, namespace=self.namespace)
        
        if inst in self.relation:
            return self.relation[inst]
        else:
            self.relation[inst] = _Relation(creator, inst, self.name)
            return self.relation[inst]
