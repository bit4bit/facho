from .field import Field

class BoundModel:
    def __init__(self, creator):
        self.creator = creator

    def create(self):
        return self.creator()

class One2Many(Field):
    def __init__(self, model, name=None, namespace=None, default=None):
        self.model = model
        self.field_name = name
        self.namespace = namespace
        self.default = default
        self.count_relations = 0
        
    def __get__(self, inst, cls):
        assert self.name is not None
        def creator():
            attribute = '%s_%d' % (self.name, self.count_relations)
            self.count_relations += 1
            return self._create_model(inst, name=self.field_name, model=self.model, attribute=attribute)

        return BoundModel(creator)
