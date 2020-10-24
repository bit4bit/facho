# uso de la libreria

modelar la factura usando **facho/fe/form.py** ver **examples/generate-invoice-invoice.py(invoice)**, instanciar las extensiones requeridas ver **examples/generate-invoice-invoice.py(extensions)**
una vez generado el objeto invoice y con las extensiones se procede a crear el XML, ejemplo:

~~~python
....
validator = form.DianResolucion0001Validator()

if not validator.validate(invoice):
  for error in validator.errors:
    raise print("ERROR:", error)
  raise RuntimeError("invoice invalid")

xml = form_xml.DIANInvoiceXML(invoice)
extensions = module.extensions(invoice)
for extension in extensions:
  xml.add_extension(extension)

form_xml.DIANWriteSigned(xml, "factura.xml", "llave privada", "frase")
~~~
