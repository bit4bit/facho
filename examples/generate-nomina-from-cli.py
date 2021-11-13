
from facho import fe

def extensions(nomina):
    return []

def nomina():
    nomina = fe.nomina.DIANNominaIndividual()

    nomina.asignar_metadata(fe.nomina.Metadata(
        secuencia=fe.nomina.NumeroSecuencia(
            numero = 'N00001',
            consecutivo=232
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
            nit='999999',
            dv=2,
            software_id='xx',
            software_sc='yy'
        )
    ))

    nomina.asignar_informacion_general(fe.nomina.InformacionGeneral(
        fecha_generacion = '2020-01-16',
        hora_generacion = '1053:10-05:00',
        tipo_ambiente = fe.nomina.InformacionGeneral.AMBIENTE_PRODUCCION,
        software_pin = '693',
        periodo_nomina = fe.nomina.PeriodoNomina(code='1'),
        tipo_moneda = fe.nomina.TipoMoneda(code='COP')
    ))

    nomina.asignar_empleador(fe.nomina.Empleador(
        nit = '700085371',
        dv = '1',
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
        numero_documento = '800199436',
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

    return nomina
