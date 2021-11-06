# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from lxml import etree
from lxml.etree import Element, SubElement, tostring
import re
from collections import defaultdict
from copy import deepcopy
from pprint import pprint

class FachoValueInvalid(Exception):
    def __init__(self, xpath):
        super().__init__('FachoValueInvalid invalid xpath %s' % (xpath))


class FachoXMLExtension:

    def build(self, fachoxml):
        raise NotImplementedError


class LXMLBuilder:
    """
    extrae la manipulacion de XML
    """
    # TODO buscar el termino mas adecuado
    # ya que son varios lo procesos que se
    # exponen en la misma clase
    #   * creacion
    #   * busquedad
    #   * comparacion

    def __init__(self, nsmap):
        self.nsmap = nsmap
        self._re_node_expr = re.compile(r'^(?P<path>((?P<ns>\w+):)?(?P<tag>[a-zA-Z0-9_-]+))(?P<attrs>\[.+\])?')
        self._re_attrs = re.compile(r'(\w+)\s*=\s*\"?(\w+)\"?')

    def match_expression(self, node_expr):
        match = re.search(self._re_node_expr, node_expr)
        return match.groupdict()

    @classmethod
    def from_string(cls, content, clean_namespaces=False):
        if clean_namespaces:
            content = re.sub(r'\<\s*[a-zA-Z\-0-9]+\s*:', '<', content)
            content = re.sub(r'\<\/\s*[a-zA-Z\-0-9]+\s*:', '</', content)

        return etree.fromstring(content)

    @classmethod
    def build_element_from_string(cls, string, nsmap):
        return Element(string, nsmap=nsmap)

    def build_element(self, tag, ns=None, attribs={}):
        attribs['nsmap'] = ns
        if ns:
            tag = '{%s}%s' % (self.nsmap[ns], tag)
        return Element(tag, **attribs)

    def build_from_expression(self, node_expr):
        match = re.search(self._re_node_expr, node_expr)
        expr = match.groupdict()
        attrs = dict(re.findall(self._re_attrs, expr['attrs'] or ''))
        attrs['nsmap'] = None
        if expr['ns'] and expr['tag']:
            ns = expr['ns']
            tag = expr['tag']
            if self.nsmap:
                node = Element('{%s}%s' % (self.nsmap[ns], tag), **attrs)
            else:
                node = Element(tag, **attrs)
            return node

        return Element(expr['tag'], **attrs)

    def _normalize_tag(self, tag):
        return re.sub(r'^(\{.+\}|.+:)', '', tag)

    def get_tag(self, elem):
        return self._normalize_tag(elem.tag)

    def same_tag(self, a, b):
        return self._normalize_tag(a) \
            == self._normalize_tag(b)

    def find_relative(self, elem, xpath, ns):
        return elem.find(xpath, ns)

    def append(self, elem, child):
        elem.append(child)

    def append_next(self, elem, slibing):
        elem.addnext(slibing)

    def remove(self, elem):
        elem.getparent().remove(elem)

    def set_text(self, elem, text):
        elem.text = text

    def xpath(self, elem, xpath, multiple=False):
        elems = elem.xpath(xpath, namespaces=self.nsmap)
        if elems:
            if multiple:
                return elems
            else:
                return elems[0]

        return None

    def get_text(self, elem):
        return elem.text

    def get_attribute(self, elem, key):
        return elem.attrib[key]

    def is_attribute(self, elem, key, value):
        return elem.get(key, False) == value

    def set_attribute(self,  elem, key, value):
        elem.attrib[key] = value

    @classmethod
    def remove_attributes(cls, elem, keys, exclude = []):
        for key in keys:
            if key in exclude:
                continue

            try:
                del elem.attrib[key]
            except KeyError:
                pass

    @classmethod
    def tostring(self, oelem, **attrs):
        elem = deepcopy(oelem)

        attrs['pretty_print'] = attrs.pop('pretty_print', False)
        attrs['encoding'] = attrs.pop('encoding', 'UTF-8')

        for el in elem.getiterator():
            keys = filter(lambda key: key.startswith('facho_'), el.keys())
            self.remove_attributes(el, keys, exclude=['facho_optional'])

            is_optional = el.get('facho_optional', 'False') == 'True'
            if is_optional and el.getchildren() == [] and el.keys() == ['facho_optional']:
                el.getparent().remove(el)

        return tostring(elem, **attrs).decode('utf-8')


class FachoXML:
    """
    Decora XML con funciones de consulta XPATH de un solo elemento
    """
    def __init__(self, root, builder=None, nsmap=None, fragment_prefix=''):
        if builder is None:
            self.builder = LXMLBuilder(nsmap)
        else:
            self.builder = builder

        self.nsmap = nsmap

        if isinstance(root, str):
            self.root = self.builder.build_element_from_string(root, nsmap)
        else:
            self.root = root

        self.fragment_prefix = fragment_prefix
        self.xpath_for = {}
        self.extensions = []
        self._validators = defaultdict(lambda: lambda v, attrs: True)

    @classmethod
    def from_string(cls, document: str, namespaces: dict() = []) -> 'FachoXML':
        xml = LXMLBuilder.from_string(document)
        return FachoXML(xml, nsmap=namespaces)

    def append_element(self, elem, new_elem):
        #elem = self.find_or_create_element(xpath, append=append)
        #self.builder.append(elem, new_elem)
        self.builder.append(elem, new_elem)

    def add_extension(self, extension):
        extension.build(self)


    def fragment(self, xpath, append=False, append_not_exists=False):
        nodes = xpath.split('/')
        nodes.pop()
        root_prefix = '/'.join(nodes)
        parent = None
        if append_not_exists:
            parent = self.get_element(xpath)

        if parent is None:
            parent = self.find_or_create_element(xpath, append=append)
        return FachoXML(parent, nsmap=self.nsmap, fragment_prefix=root_prefix)

    def register_alias_xpath(self, alias, xpath):
        self.xpath_for[alias] = xpath

    def _translate_xpath_for(self, xpath):
        if xpath in self.xpath_for:
            xpath = self.xpath_for[xpath]
        return xpath

    def _normalize_xpath(self, xpath):
        return xpath.replace('//', '/')

    def _path_xpath_for(self, xpath):
        return self._normalize_xpath(self._translate_xpath_for(xpath))

    def placeholder_for(self, xpath, append=False, optional=False):
        elem = self.find_or_create_element(xpath, append)
        if optional:
            elem.set('facho_optional', 'True')
        elem.set('facho_placeholder', 'True')
        return elem

    def replacement_for(self, xpath, new_xpath, content, **attrs):
        elem = self.get_element(xpath)
        self.builder.remove(elem)
        return self.set_element(new_xpath, content, **attrs)

    def find_or_create_element(self, xpath, append=False):
        """
        @param xpath ruta xpath para crear o consultar de un solo elemendo
        @param append True si se debe adicionar en la ruta xpath indicada
        @return elemento segun self.builder
        """
        xpath = self._path_xpath_for(xpath)
        node_paths = xpath.split('/')
        node_paths.pop(0) #remove empty /
        root_tag = node_paths.pop(0)

        root_node = self.builder.build_from_expression(root_tag)
        if xpath.startswith('.'):
            # restaurar ya que no es la raiz y asignar actual como raiz
            node_paths.insert(0, root_tag)
            root_node = self.root
            
        if not self.builder.same_tag(root_node.tag, self.root.tag):
            
            raise ValueError('xpath %s must be absolute to /%s' % (xpath, self.root.tag))

        # crea jerarquia segun xpath indicado
        parent = None
        current_elem = self.root
        node_tag = node_paths.pop(-1)

        for node_path in node_paths:
            node_expr = self.builder.match_expression(node_path)
            node = self.builder.build_from_expression(node_path)

            child = self.builder.find_relative(current_elem, node_expr['path'], self.nsmap)

            parent = current_elem
            if child is not None:
                current_elem = child
            else:
                self.builder.append(current_elem, node)
                current_elem = node

        node_expr = self.builder.match_expression(node_tag)
        node = self.builder.build_from_expression(node_tag)
        child = self.builder.find_relative(current_elem, node_expr['path'], self.nsmap)
        parent = current_elem
        if child is not None:
            current_elem = child
           
        if parent == current_elem:
            self.builder.append(parent, node)
            return node

        # se fuerza la adicion como un nuevo elemento
        if append:
            last_slibing = None
            for child in parent.getchildren():
                if child.tag == node_tag:
                    last_slibing = child

            # si no ahi primos se adiciona como hijo
            if last_slibing is None:
                self.builder.append(parent, node)
                return node

            if self.builder.is_attribute(last_slibing, 'facho_placeholder', 'True'):
                self._remove_facho_attributes(last_slibing)
                return last_slibing 
            self.builder.append_next(last_slibing, node)
            return node

        if child is None:
            self.builder.append(current_elem, node)
            return node

        self._remove_facho_attributes(current_elem)
        return current_elem

    def set_element_validator(self, xpath, validator = False):
        """
        validador al asignar contenido a xpath indicado

        @param xpath ruta tipo XPath
        @param validator callback(content, attributes)
        """

        key = self._path_xpath_for(xpath)
        if not validator:
            self._validators[key] = lambda v, attrs: True
        else:
            self._validators[key] = validator
        
    def set_element(self, xpath, content, **attrs):
        """
        asigna contenido ubicado por ruta tipo XPATH.
        @param xpath ruta tipo XPATH
        @param content contenido
        @return lxml.Element
        """
        xpath = self._path_xpath_for(xpath)
        format_ = attrs.pop('format_', '%s')
        append_ = attrs.pop('append_', False)
        elem = self.find_or_create_element(xpath, append=append_)

        validator = self._validators[xpath]

        if not validator(content, attrs):
            raise FachoValueInvalid(xpath)

        if content:
            self.builder.set_text(elem, format_ % content)
        for k, v in attrs.items():
            if v is not None or str(v) != 'None':
                self.builder.set_attribute(elem, k, str(v))

        return elem

    def set_attributes(self, xpath, **attrs):
        """
        asigna atributos a elemento xml ubicador por ruta XPATH
        @param xpath ruta tipo  XPATH
        @param keywords clave valor de los atributos
        """
        xpath = self._path_xpath_for(xpath)
        elem = self.get_element(xpath)

        if elem is None:
            raise ValueError("xpath %s not found" % (xpath))

        for k, v in attrs.items():
            if v is not None or str(v) != 'None':
                self.builder.set_attribute(elem, k, str(v))
        return self

    def get_element_attribute(self, xpath, attribute, multiple=False):
        elem = self.get_element(xpath, multiple=multiple)

        if elem is None:
            raise ValueError("xpath %s not found" % (xpath))

        if multiple:
            vals = []
            for e in elem:
                vals.append(self.builder.get_attribute(e, attribute))
            return vals
        else:
            return self.builder.get_attribute(elem, attribute)

    def get_element(self, xpath, multiple=False):
        xpath = self.fragment_prefix + self._path_xpath_for(xpath)
        return self.builder.xpath(self.root, xpath, multiple=multiple)

    def get_element_text(self, xpath, format_=str, multiple=False):
        xpath = self.fragment_prefix + self._path_xpath_for(xpath)
        elem = self.builder.xpath(self.root, xpath, multiple=multiple)
        if multiple:
            vals = []
            for e in elem:
                text = self.builder.get_text(e)
                if text is not None:
                    vals.append(format_(text))
            return vals
        else:
            text = self.builder.get_text(elem)
            if text is None:
                return None
            return format_(text)

    def get_element_text_or_attribute(self, xpath, default=None, multiple=False, raise_on_fail=False):
        parts = xpath.split('/')
        is_attribute =  parts[-1].startswith('@')
        if is_attribute:
            attribute_name = parts.pop(-1).lstrip('@')
            element_path = "/".join(parts)
            try:
                val = self.get_element_attribute(element_path, attribute_name, multiple=multiple)
                if val is None:
                    return default
                return val
            except KeyError as e:
                if raise_on_fail:
                    raise e
                return default
            except ValueError as e:
                if raise_on_fail:
                    raise e
                return default
        else:
            try:
                val = self.get_element_text(xpath, multiple=multiple)
                if val is None:
                    return default
                return val
            except ValueError as e:
                if raise_on_fail:
                    raise e
                return default

    def get_elements_text_or_attributes(self, xpaths, raise_on_fail=True):
        """
        returna el contenido o attributos de un conjunto de XPATHS
        si algun XPATH es una tupla se retorna el primer elemento del mismo.
        """
        vals = []
        for xpath in xpaths:
            if isinstance(xpath, tuple):
                val = xpath[0]
            else:
                val = self.get_element_text_or_attribute(xpath, raise_on_fail=raise_on_fail)
            vals.append(val)
        return vals

    def exist_element(self, xpath):
        elem = self.get_element(xpath)

        if elem is None:
            return False

        if elem.get('facho_placeholder') == 'True':
            return False

        if elem.get('facho_optional') == 'True':
            return False

        return True

    def _remove_facho_attributes(self, elem):
        self.builder.remove_attributes(elem, ['facho_optional', 'facho_placeholder'])

    def tostring(self, **kw):
        return self.builder.tostring(self.root, **kw)

    def __str__(self):
        return self.tostring()
