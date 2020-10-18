import os.path

import xmlschema


def path_for_xsd(dirname, xsdname):
    data_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(data_dir, dirname, xsdname)

UBLInvoice= xmlschema.XMLSchema(path_for_xsd('maindoc', 'UBL-Invoice-2.1.xsd'))

def validate(xml, schema):
    schema.validate(xml)
