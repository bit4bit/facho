# facho

libreria facturacion electronica colombia

# INSTALACION

~~~bash
$ pip install git+https://git.disroot.org/Etrivial/facho
~~~

# LINEA COMANDOS

al instalar el paquete se genera el comando *facho*


## COMENTARIOS

  * http://facturasyrespuestas.com/2342/error-al-enviar-set-de-pruebas-usando-sendtestsetasync

# CÓMO CONTRIBUIR?

## INSTALAR USANDO python develop

este enlaza el ejecutable **facho** en lugar de copiarlo.

## CUMPLIR ANEXO TECNICO

el archivo **docs/DIAN/Anexo_Tecnico_Factura_Electronica_Vr1_7_2020.pdf** describe la implementación de la
facturación, la libreria **facho.py** permite crear elementos xml usando XPath-Like con el proposito
de facilitar la relación entre el anexo y la implementación.

  * facho/form.py: generación de Invoice XML.
  * facho/fe.py: extensiones XML, ejemplo CUFE, Firma, etc..