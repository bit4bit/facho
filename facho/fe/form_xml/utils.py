from .. import fe

__all__ = ['DIANWrite', 'DIANWriteSigned']

def DIANWrite(xml, filename):
    document = xml.tostring(xml_declaration=True, encoding='UTF-8')
    with open(filename, 'w') as f:
        f.write(document)

        
def DIANWriteSigned(xml, filename, private_key, passphrase, use_cache_policy=False, dian_signer=None):
    document = xml.tostring(xml_declaration=True, encoding='UTF-8').encode('utf-8')
    if dian_signer is None:
        dian_signer = fe.DianXMLExtensionSigner

    signer = dian_signer(private_key, passphrase=passphrase, mockpolicy=use_cache_policy)

    with open(filename, 'w') as f:
        f.write(signer.sign_xml_string(document))
