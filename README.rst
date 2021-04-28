=====
facho
=====

Libreria para facturacion electronica colombia.

- facho/facho.py: abstracion para manipulacion del XML
- facho/fe/form.py: abstraciones para creacion de facturas.
- facho/fe/form_xml.py(DIANInvoiceXML): decora abstraciones con campos requeridos por la DIAN.
- facho/fe/fe.py(DianXMLExtensionSigner): extension para firmar xml
- facho/fe/client/dian.py(DianClient): cliente para consultas sincronicas a API de DIAN


INSTALACION
===========


usando pip::
  
   pip install git+https://git.disroot.org/Etrivial/facho

CLI
===

tambien se provee linea de comandos **facho** para generacion, firmado y envio de documentos::
  facho --help

CONTRIBUIR
==========

ver **CONTRIBUTING.rst**

USO
===

ver **USAGE.rst**


DIAN HABILITACION
=================

guia oficial actualizada al 2020-04-20: https://www.dian.gov.co/fizcalizacioncontrol/herramienconsulta/FacturaElectronica/Facturaci%C3%B3n_Gratuita_DIAN/Documents/Guia_usuario_08052019.pdf#search=numeracion
