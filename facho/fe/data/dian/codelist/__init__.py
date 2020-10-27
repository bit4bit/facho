import os.path

from lxml import etree


DATA_DIR = os.path.dirname(os.path.abspath(__file__))


class CodeList:

    def __init__(self, filename, primary_column, name_column):
        self.short_name = ''
        self.long_name = ''
        self.version = 1
        self.canonical_uri = ''
        self.canonical_version_uri = ''
        self.location_uri = ''

        self.name_column = name_column
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

    def __contains__(self, key):
        return key in self.rows

    def by_name(self, name):
        for k, v in self.rows.items():
            if v[self.name_column] == name:
                return v
        raise KeyError

    def update(self, other):
        for k, v in other.rows.items():
            self.rows[k] = v
        return self

# nombres de variables igual a ./Identification/ShortName
# TODO: garantizar unica carga en python

__all__ = ['TipoOrganizacion',
           'TipoResponsabilidad',
           'TipoAmbiente',
           'TipoDocumento',
           'TipoImpuesto',
           'CodigoPrecioReferencia',
           'MediosPago',
           'RegimenFiscal',
           'Municipio',
           'Departamento']

def path_for_codelist(name):
    return os.path.join(DATA_DIR, name)

TipoOrganizacion = CodeList(path_for_codelist('TipoOrganizacion-2.1.gc'), 'code', 'name')
TipoResponsabilidad = CodeList(path_for_codelist('TipoResponsabilidad-2.1.gc'), 'code', 'name')\
    .update(CodeList(path_for_codelist('TipoResponsabilidad-2.1.custom.gc'), 'code', 'name'))
TipoAmbiente = CodeList(path_for_codelist('TipoAmbiente-2.1.gc'), 'code', 'name')
TipoDocumento = CodeList(path_for_codelist('TipoDocumento-2.1.gc'), 'code', 'name')
TipoImpuesto = CodeList(path_for_codelist('TipoImpuesto-2.1.gc'), 'code', 'name')
CodigoPrecioReferencia = CodeList(path_for_codelist('CodigoPrecioReferencia-2.1.gc'), 'code', 'name')
MediosPago = CodeList(path_for_codelist('MediosPago-2.1.gc'), 'code', 'name')
RegimenFiscal = CodeList(path_for_codelist('RegimenFiscal-2.1.custom.gc'), 'code', 'name')
TipoOperacionF = CodeList(path_for_codelist('TipoOperacionF-2.1.gc'), 'code', 'name')\
    .update(CodeList(path_for_codelist('TipoOperacionF-2.1.custom.gc'), 'code', 'name'))
Municipio = CodeList(path_for_codelist('Municipio-2.1.gc'), 'code', 'name')
Departamento = CodeList(path_for_codelist('Departamentos-2.1.gc'), 'code', 'name')
