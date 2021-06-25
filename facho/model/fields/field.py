class Field:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None
        return inst._fields[self.name]

    def __set__(self, inst, value):
        assert self.name is not None
        inst._fields[self.name] = value

    def _set_namespace(self, inst, name, namespaces):
        if name is None:
            return

        if name not in namespaces:
            raise KeyError("namespace %s not found" % (name))
        inst._namespace_prefix = name

    def _call(self, inst, method, *args):
        call = getattr(inst, method or '', None)

        if callable(call):
            return call(*args)

    def _create_model(self, inst, name=None, model=None):
        try:
            return inst._fields[self.name]
        except KeyError:
            if model is not None:
                obj = model()
            else:
                obj = self.model()
            if name is not None:
                obj.__name__ = name
            self._set_namespace(obj, self.namespace, inst.__namespace__)
            inst._fields[self.name] = obj
            return obj

    def _changed_field(self, inst, name, value):
        for fun in inst._on_change_fields[name]:
            getattr(inst, fun)(name, value)
            
