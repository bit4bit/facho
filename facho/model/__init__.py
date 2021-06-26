from .fields import Field
from collections import defaultdict

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
        obj._on_change_fields = defaultdict(list)
        
        def on_change_fields_for_function():
            # se recorre arbol buscando el primero
            for parent_cls in type(obj).__mro__:
                for parent_attr in dir(parent_cls):
                    parent_meth = getattr(parent_cls, parent_attr, None)
                    if not callable(parent_meth):
                        continue
                    on_changes = getattr(parent_meth, 'on_changes', None)
                    if on_changes:
                        return (parent_meth, on_changes)
            return (None, [])

        # forzamos registros de campos al modelo
        # al instanciar
        for (key, v) in type(obj).__dict__.items():
                
            if isinstance(v, fields.Attribute) or isinstance(v, fields.Many2One) or isinstance(v, fields.Function):
                if hasattr(v, 'default') and v.default is not None:
                    setattr(obj, key, v.default)
                
                # register callbacks for changes
                (fun, on_change_fields) = on_change_fields_for_function()
                for field in on_change_fields:
                    obj._on_change_fields[field].append(fun)
        
        return obj

    def _set_attribute(self, field, name, value):
        self._xml_attributes[field] = (name, value)

    def __setitem__(self, key, val):
        self._xml_attributes[key] = val

    def __getitem__(self, key):
        return self._xml_attributes[key]

    def _get_field(self, name):
        return self._fields[name]

    def _set_field(self, name, field):
        field.name = name
        self._fields[name] = field

    def _set_content(self, value):
        default = self.__default_set__(value)
        if default is not None:
            self._text = str(default)

    def _hook_before_xml(self):
        self.__before_xml__()
        for field in self._fields.values():
            if hasattr(field, '__before_xml__'):
                field.__before_xml__()

    def to_xml(self):
        """
        Genera xml del modelo y sus relaciones
        """
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

        for value in self._fields.values():
            if hasattr(value, 'to_xml'):
                content += value.to_xml()
            elif isinstance(value, str):
                content += value
        content += self._text

        if content == "":
            return "<%s%s%s/>" % (ns, tag, attributes)
        else:
            return "<%s%s%s>%s</%s%s>" % (ns, tag, attributes, content, ns, tag)

class Model(ModelBase):
    def __before_xml__(self):
        """
        Ejecuta antes de generar el xml, este
        metodo sirve para realizar actualizaciones
        en los campos en el ultimo momento
        """
        pass

    def __default_set__(self, value):
        """
        Al asignar un valor al modelo atraves de una relacion (person.relation = '33')
        se puede personalizar como hacer esta asignacion.
        """
        return value

        
