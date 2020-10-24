=====
facho
=====

Libreria para facturacion electronica colombia.

- facho/facho.py: abstracion para manipulacion del XML
- facho/fe/form.py: abstraciones para creacion de facturas.
- facho/fe/form_xml.py(DIANInvoiceXML): decora abstraciones con campos requeridos por la DIAN.
- facho/fe/fe.py(DianXMLExtensionSigner): extension para firmar xml
- facho/fe/client/dian.py(DianClient): cliente para consultas sincronicas a API de DIAN


DIAN HABILITACION
=================

guia oficial actualizada al 2020-04-20: https://www.dian.gov.co/fizcalizacioncontrol/herramienconsulta/FacturaElectronica/Facturaci%C3%B3n_Gratuita_DIAN/Documents/Guia_usuario_08052019.pdf#search=numeracion


ERROR X509SerialNumber
======================


lxml.etree.DocumentInvalid: Element '{http://www.w3.org/2000/09/xmldsig#}X509SerialNumber': '632837201711293159666920255411738137494572618415' is not a valid value of the atomic type 'xs:integer'

Actualmente el xmlschema usado por xmlsig para el campo X509SerialNumber es tipo
integer ahi que parchar manualmente a tipo string, en el archivo site-packages/xmlsig/data/xmldsig-core-schema.xsd.
