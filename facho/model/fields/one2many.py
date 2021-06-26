from .field import Field

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

        return getattr(self.__dict__['_obj'], name)

    def __setattr__(self, attr, value):
        # TODO(bit4bit) hacemos proxy al sistema de notificacion de cambios
        # algo burdo, se usa __dict__ para saltarnos el __getattr__ y generar un fallo por recursion
        for fun in self.__dict__['_inst']._on_change_fields[self.__dict__['_attribute']]:
            fun(self.__dict__['_inst'], self.__dict__['_attribute'], value)

        return setattr(self._obj, attr, value)

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
    def __init__(self, model, name=None, namespace=None, default=None):
        self.model = model
        self.field_name = name
        self.namespace = namespace
        self.default = default
        self.relation = None
        
    def __get__(self, inst, cls):
        assert self.name is not None

        def creator(attribute):
            return self._create_model(inst, name=self.field_name, model=self.model, attribute=attribute)
        
        if self.relation:
            return self.relation
        else:
            self.relation = _Relation(creator, inst, self.name)
            return self.relation
