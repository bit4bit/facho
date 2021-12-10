from dataclasses import dataclass
import datetime

from facho import fe

class Habilitacion:

    @dataclass
    class Metadata:
        software_pin: str
        software_id: str
        nit: str
        dv: str

    def __init__(self, metadata):
        self.metadata = metadata

    def generar(self, zipname, fecha):
        nominas = []
        dianzip = fe.DianZIP(open(zipname, 'w'))

        fechabase = datetime.datetime.now()
        consecutivo = 0
        for _ in range(1, 11):
            consecutivo += 1
            fechabase += datetime.timedelta(days=1)
            nomina = self._crear_nomina_individual()

            # pag 96
            nombre = "nie%010d%s%08x.xml" % (int(self.nit), fecha.strftime('%s'), consecutivo)
        
    def _crear_nomina_individual_reemplazar(self, nomina, fechabase):
        metadata = self.metadata

        fecha = fechabase.strftime('%Y-%m-%d')

        nomina_ajuste = fe.nomina.DIANNominaIndividualDeAjuste.Reemplazar()
        self._poblar_nomina(nomina_ajuste, metadata, fecha, prefijo='R')
        informacion_general = nomina.informacion_general()
        
        
    def _poblar_nomina(self, nomina, metadata, fecha, prefijo='N', consecutivo='0001'):
        nomina.asignar_fecha_pago(fecha)

        nomina.asignar_metadata(fe.nomina.Metadata(
            secuencia=fe.nomina.NumeroSecuencia(
                prefijo=prefijo,
                consecutivo=consecutivo
            ),
            lugar_generacion=fe.nomina.Lugar(
                pais = fe.nomina.Pais(
                    code = 'CO'
                ),
                departamento = fe.nomina.Departamento(
                    code = '05'
                ),
                municipio = fe.nomina.Municipio(
                    code = '05001'
                ),
            ),
            proveedor=fe.nomina.Proveedor(
                nit=metadata.nit,
                dv=metadata.dv,
                software_id=metadata.software_id,
                software_pin=metadata.software_pin
            )
        ))

        nomina.asignar_periodo(fe.nomina.Periodo(
            fecha_ingreso=fecha,
            fecha_liquidacion_inicio=fecha,
            fecha_liquidacion_fin=fecha,
            fecha_generacion=fecha,
        ))
        
        nomina.asignar_informacion_general(fe.nomina.InformacionGeneral(
            fecha_generacion = fecha,
            hora_generacion = '20:09:00-05:00',
            tipo_ambiente = fe.nomina.InformacionGeneral.AMBIENTE_PRUEBAS,
            software_pin = metadata.software_pin,
            periodo_nomina = fe.nomina.PeriodoNomina(code='1'),
            tipo_moneda = fe.nomina.TipoMoneda(code='COP')
        ))

        nomina.asignar_pago(fe.nomina.Pago(
            forma=fe.nomina.FormaPago(
                code='1',
            ),
            metodo=fe.nomina.MetodoPago(
                code='10'
            )
        ))
        nomina.asignar_empleador(fe.nomina.Empleador(
            nit = metadata.nit,
            dv = '0',
            pais = fe.nomina.Pais(
                code = 'CO'
            ),
            departamento = fe.nomina.Departamento(
                code = '05'
            ),
            municipio = fe.nomina.Municipio(
                code = '05001'
            ),
            direccion = 'calle etrivial'
        ))

        nomina.asignar_trabajador(fe.nomina.Trabajador(
            tipo_contrato = fe.nomina.TipoContrato(
                code = '1'
            ),
            alto_riesgo = False,
            tipo_documento = fe.nomina.TipoDocumento(
                code = '11'
            ),
            primer_apellido = 'gnu',
            segundo_apellido = 'emacs',
            primer_nombre = 'facho',
            lugar_trabajo = fe.nomina.LugarTrabajo(
                pais = fe.nomina.Pais(code='CO'),
                departamento = fe.nomina.Departamento(code='05'),
                municipio = fe.nomina.Municipio(code='05001'),
                direccion = 'calle facho'
            ),
            numero_documento = metadata.nit,
            tipo = fe.nomina.TipoTrabajador(
                code = '01'
            ),
            salario_integral = True,
            sueldo = fe.nomina.Amount(1_500_000)
        ))
        
        nomina.adicionar_devengado(fe.nomina.DevengadoBasico(
            dias_trabajados = 60,
            sueldo_trabajado = fe.nomina.Amount(3_500_000)
        ))

        nomina.adicionar_deduccion(fe.nomina.DeduccionSalud(
            porcentaje = fe.nomina.Amount(19),
            deduccion = fe.nomina.Amount(1_000_000)
        ))

        nomina.adicionar_deduccion(fe.nomina.DeduccionFondoPension(
            porcentaje=fe.nomina.Amount(1),
            deduccion=fe.nomina.Amount(10)
        ))

    def _crear_nomina_individual(self, fechabase):
        metadata = self.metadata

        fecha = fechabase.strftime('%Y-%m-%d')

        nomina = fe.nomina.DIANNominaIndividual()
        self._poblar_nomina(nomina, metadata, fecha)
                
