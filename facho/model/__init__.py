from .fields import Field
from collections import defaultdict

class ModelMeta(type):
    def __new__(cls, name, bases, ns):
        new = type.__new__(cls, name, bases, ns)

        # mapeamos asignacion en declaracion de clase
        # a attributo de objeto
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
        obj._value = None
        obj._namespace_prefix = None
        obj._on_change_fields = defaultdict(list)
        obj._order_fields = []
        
        def on_change_fields_for_function():
            # se recorre arbol de herencia buscando attributo on_changes
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
            if isinstance(v, fields.Field):
                obj._order_fields.append(key)

            if isinstance(v, fields.Attribute) or isinstance(v, fields.Many2One) or isinstance(v, fields.Function) or isinstance(v, fields.Amount):
                if hasattr(v, 'default') and v.default is not None:
                    setattr(obj, key, v.default)
                if hasattr(v, 'create') and v.create == True:
                    setattr(obj, key, '')

                # register callbacks for changes
                (fun, on_change_fields) = on_change_fields_for_function()
                for field in on_change_fields:
                    obj._on_change_fields[field].append(fun)


        # post inicializacion del objeto
        obj.__setup__()
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
            self._value = default

    def to_xml(self):
        """
        Genera xml del modelo y sus relaciones
        """
        def _hook_before_xml():
            self.__before_xml__()
            for field in self._fields.values():
                if hasattr(field, '__before_xml__'):
                    field.__before_xml__()
                    
        _hook_before_xml()

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

        ordered_fields = {}
        for name in self._order_fields:
            if name in self._fields:
                ordered_fields[name] = True
            else:
                for key in self._fields.keys():
                    if key.startswith(name):
                        ordered_fields[key] = True

        for name in ordered_fields.keys():
            value = self._fields[name]
            # al ser virtual no adicinamos al arbol xml
            if hasattr(value, 'virtual') and value.virtual:
                continue

            if hasattr(value, 'to_xml'):
                content += value.to_xml()
            elif isinstance(value, str):
                content += value

        if self._value is not None:
            content += str(self._value)

        if content == "":
            return "<%s%s%s/>" % (ns, tag, attributes)
        else:
            return "<%s%s%s>%s</%s%s>" % (ns, tag, attributes, content, ns, tag)

    def __str__(self):
        return self.to_xml()


class Model(ModelBase):
    """
    Model clase que representa el modelo
    """

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

    def __default_get__(self, name, value):
        """
        Al obtener el valor atraves de una relacion (age = person.age)
        Retorno de valor por defecto
        """
        return value

    def __setup__(self):
        """
        Inicializar modelo
        """
        
