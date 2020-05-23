import os.path

from lxml import etree


DATA_DIR = os.path.dirname(os.path.abspath(__file__))


class CodeList:

    def __init__(self, filename, primary_column):
        self.short_name = ''
        self.long_name = ''
        self.version = 1
        self.canonical_uri = ''
        self.canonical_version_uri = ''
        self.location_uri = ''
        
        self.rows = {}
        self._load(filename, primary_column)

    def _load(self, filename, primary_column):
        tree = etree.parse(filename)

        #obtener identificadores...
        self.short_name = tree.find('./Identification/ShortName').text
        self.long_name = tree.find('./Identification/LongName').text
        self.version = tree.find('./Identification/Version').text
        self.canonical_uri = tree.find('./Identification/CanonicalUri').text
        self.canonical_version_uri = tree.find('./Identification/CanonicalVersionUri').text
        self.location_uri = tree.find('./Identification/LocationUri').text

        #obtener registros...
        for row in tree.findall('./SimpleCodeList/Row'):
            new_row = self.xmlrow_to_dict(row)
            primary_key = new_row[primary_column]
            self.rows[primary_key] = new_row.copy()

    def xmlrow_to_dict(self, xmlrow):
        row = {}

        #construir registro...
        for value in xmlrow.getchildren():
            row[value.attrib['ColumnRef']] = value.getchildren()[0].text

        return row
    
    def __getitem__(self, key):
        return self.rows[str(key)]


# nombres de variables igual a ./Identification/ShortName
# TODO: garantizar unica carga en python

__all__ = ['TipoOrganizacion',
           'TipoResponsabilidad',
           'TipoAmbiente']

TipoOrganizacion = CodeList(os.path.join(DATA_DIR, 'TipoOrganizacion-2.1.gc'), 'name')
TipoResponsabilidad = CodeList(os.path.join(DATA_DIR, 'TipoResponsabilidad-2.1.gc'), 'name')
TipoAmbiente = CodeList(os.path.join(DATA_DIR, 'TipoAmbiente-2.1.gc'), 'name')
