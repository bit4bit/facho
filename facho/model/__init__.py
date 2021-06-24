
class ModelMeta(type):
    def __new__(cls, name, bases, ns):
        new = type.__new__(cls, name, bases, ns)
        if '__name__' in ns:
            new.__name__ = ns['__name__']
        if '__namespace__' in ns:
            new.__namespace__ = ns['__namespace__']
        else:
            new.__namespace__ = {}
            
        return new

class ModelBase(object, metaclass=ModelMeta):

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._xml_attributes = {}
        obj._fields = {}
        obj._text = ""
        obj._namespace_prefix = None
        
        return obj

    def __setitem__(self, key, val):
        self._xml_attributes[key] = val

    def __getitem__(self, key):
        return self._xml_attributes[key]

    def __before_xml__(self):
        pass

    def _hook_before_xml(self):
        self.__before_xml__()
        for field in self._fields.values():
            if hasattr(field, '__before_xml__'):
                field.__before_xml__()

    def to_xml(self):
        self._hook_before_xml()

        tag = self.__name__
        ns = ''
        if self._namespace_prefix is not None:
            ns = "%s:" % (self._namespace_prefix)

        pair_attributes = ["%s=\"%s\"" % (k, v) for (k, v) in self._xml_attributes.values()]

        for (prefix, url) in self.__namespace__.items():
            pair_attributes.append("xmlns:%s=\"%s\"" % (prefix, url))
        attributes = ""
        if pair_attributes:
            attributes = " " + " ".join(pair_attributes)

        content = ""

        for name, value in self._fields.items():
            if hasattr(value, 'to_xml'):
                print(self._fields)
                content += value.to_xml()
            elif isinstance(value, str):
                content += value
        content += self._text

        if content == "":
            return "<%s%s%s/>" % (ns, tag, attributes)
        else:
            return "<%s%s%s>%s</%s%s>" % (ns, tag, attributes, content, ns, tag)

class Model(ModelBase):
    pass
        
