from .. import fe

__all__ = ['AttachedDocument']

class AttachedDocument():

    def __init__(self, id):
        schema = 'urn:oasis:names:specification:ubl:schema:xsd:AttachedDocument-2'
        self.fexml = fe.FeXML('AttachedDocument', schema)
        self.fexml.set_element('./cbc:ID', id)

    def toFachoXML(self):
        return self.fexml
        
