from facho import facho

import zeep
from zeep.wsse.username import UsernameToken


import urllib.request
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List
import http.client
import hashlib
import secrets
import base64

__all__ = ['DianClient',
           'ConsultaResolucionesFacturacionPeticion',
           'ConsultaResolucionesFacturacionRespuesta']

class SOAPService:

    def get_wsdl(self):
        raise NotImplementedError()

    def get_service(self):
        raise NotImplementedError()

    def builder_response(self, as_dict):
        raise NotImplementedError()
    
    def todict(self):
        return asdict(self)

@dataclass
class ConsultaResolucionesFacturacionRespuesta:

    @dataclass
    class RangoFacturacion:
        NumeroResolucion: str
        FechaResolucion: datetime
        Prefijo: str
        RangoInicial: int
        RangoFinal: int
        FechaVigenciaDesde: datetime
        FechaVigenciaHasta: datetime
        ClaveTecnica: str
        
    CodigoOperacion: str
    DescripcionOperacion: str
    IdentificadorOperacion: str
    RangoFacturacion: List[RangoFacturacion]


    @classmethod
    def fromdict(cls, data):
        return cls(
            data['CodigoOperacion'],
            data['DescripcionOperacion'],
            data['IdentificadorOperacion'],
            data['RangoFacturacion']
        )


@dataclass
class ConsultaResolucionesFacturacionPeticion(SOAPService):
    NITObligadoFacturarElectronicamente: str
    NITProveedorTecnologico: str
    IdentificadorSoftware: str

    def get_wsdl(self):
        return 'https://facturaelectronica.dian.gov.co/servicios/B2BIntegrationEngine-servicios/FacturaElectronica/consultaResolucionesFacturacion.wsdl'

    def get_service(self):
        return 'ConsultaResolucionesFacturacion'
    
    def build_response(self, as_dict):
        return ConsultaResolucionesFacturacionRespuesta.fromdict(as_dict)


class DianClient:

    def __init__(self, user, password):
        self._username = user
        self._password = password

    def _open(self, service):
        return zeep.Client(service.get_wsdl(), wsse=UsernameToken(self._username, self._password))

    def _remote_service(self, conn, service):
        return conn.service[service.get_service()]

    def _close(self, conn):
        return

    def request(self, service):
        if not isinstance(service, SOAPService):
            raise TypeError('service not type SOAPService')

        client = self._open(service)
        method = self._remote_service(client, service)
        resp = method(**service.todict())
        self._close(client)

        return service.build_response(resp)

    

