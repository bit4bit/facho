uso de la libreria
==================

**facho** es tanto una libreria para modelar y generar los documentos xml requeridos para la facturacion,
asi como una herramienta de **consola** para facilitar algunas actividades como: generaciones de xml
apartir de una especificacion en python, comprimir y enviar archivos según el SOAP vigente.

**facho** es diseñado para ser usado en conjunto con el documento **docs/DIAN/Anexo_Tecnico_Factura_Electronica_Vr1_7_2020.pdf**, ya que en gran medida sigue la terminologia presente en este.


Para ejemplos ver **examples/** .

En terminos generales seria modelar la factura usando **facho/fe/form.py**, instanciar las extensiones requeridas ver **facho/fe/fe.py** y
una vez generado el objeto invoice y las extensiones requeridas se procede a crear el XML, ejemplo:

~~~python
....
xml = form_xml.DIANInvoiceXML(invoice)
extensions = module.extensions(invoice)
for extension in extensions:
  xml.add_extension(extension)

form_xml.DIANWriteSigned(xml, "factura.xml", "llave privada", "frase")
~~~
