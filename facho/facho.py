# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from lxml import etree
from lxml.etree import Element, SubElement, tostring
import re


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

    def remove(self, elem):
        elem.getparent().remove(elem)

    def set_text(self, elem, text):
        elem.text = text

    def xpath(self, elem, xpath):
        elems = elem.xpath(xpath, namespaces=self.nsmap)
        if elems:
            return elems[0]

        return None

    def get_text(self, elem):
        return elem.text

    def set_attribute(self,  elem, key, value):
        elem.attrib[key] = value

    @classmethod
    def tostring(self, elem, **attrs):
        attrs['pretty_print'] = attrs.pop('pretty_print', False)
        attrs['encoding'] = attrs.pop('encoding', 'UTF-8')
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

    def placeholder_for(self, xpath, append=False):
        return self.find_or_create_element(xpath, append)

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

        # se fuerza la adicion como un nuevo elemento
        if append:
            node = self.builder.build_from_expression(node_paths[-1])
            self.builder.append(parent, node)
            return node

        return current_elem

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
        if content:
            self.builder.set_text(elem, format_ % content)
        for k, v in attrs.items():
            self.builder.set_attribute(elem, k, v)
        return elem

    def set_attributes(self, xpath, **attrs):
        """
        asigna atributos a elemento xml ubicador por ruta XPATH
        @param xpath ruta tipo  XPATH
        @param keywords clave valor de los atributos
        """
        xpath = self._path_xpath_for(xpath)
        elem = self.get_element(xpath)
        for k, v in attrs.items():
            self.builder.set_attribute(elem, k, v)
        return self

    def get_element(self, xpath):
        xpath = self.fragment_prefix + self._path_xpath_for(xpath)
        return self.builder.xpath(self.root, xpath)

    def get_element_text(self, xpath, format_=str):
        xpath = self.fragment_prefix + self._path_xpath_for(xpath)
        elem = self.builder.xpath(self.root, xpath)
        if elem is None:
            raise AttributeError('xpath %s invalid' % (xpath))

        text = self.builder.get_text(elem)
        return format_(text)

    def tostring(self, **kw):
        return self.builder.tostring(self.root, **kw)

    def __str__(self):
        return self.tostring()
