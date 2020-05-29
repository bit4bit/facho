from facho import facho

import zeep
from zeep.wsse.username import UsernameToken
from .wsse.signature import Signature, BinarySignature
from zeep.wsa import WsAddressingPlugin
import xmlsec
import urllib.request
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List
import http.client
import hashlib
import secrets
import base64

from . import zeep_plugins

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

@dataclass
class SendBillAsync:
    fileName: str
    contentFile: str

    def get_wsdl(self):
        return 'https://colombia-dian-webservices-input-sbx.azurewebsites.net/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'SendBillAsync'

    def build_response(self, as_dict):
        return {}



@dataclass
class SendTestSetAsync(SOAPService):
    fileName: str
    contentFile: str
    testSetId: str = ''

    def get_wsdl(self):
        return 'https://colombia-dian-webservices-input-sbx.azurewebsites.net/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'SendTestSetAsync'

    def build_response(self, as_dict):
        return {}

@dataclass
class SendBillSync(SOAPService):
    fileName: str
    contentFile: bytes

    def get_wsdl(self):
        return 'https://colombia-dian-webservices-input-sbx.azurewebsites.net/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'SendBillSync'

    def build_response(self, as_dict):
        return {}


@dataclass
class GetStatus(SOAPService):
    trackId: bytes

    def get_wsdl(self):
        return 'https://colombia-dian-webservices-input-sbx.azurewebsites.net/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'GetStatus'

    def build_response(self, as_dict):
        return {}


class Habilitacion:
    WSDL = 'https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc?wsdl'

    class SendBillSync(SendBillSync):
        def get_wsdl(self):
            return Habilitacion.WSDL

    class SendTestSetAsync(SendTestSetAsync):
        def get_wsdl(self):
            return Habilitacion.WSDL

    class GetStatus(GetStatus):
        def get_wsdl(self):
            return Habilitacion.WSDL
        

class DianGateway:

    def _open(self, service):
        raise NotImplementedError()

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


class DianClient(DianGateway):

    def __init__(self, user, password):
        self._username = user
        self._password = password

    def _open(self, service):
        return zeep.Client(service.get_wsdl(), wsse=UsernameToken(self._username, self._password))

    
class DianSignatureClient(DianGateway):

    def __init__(self, private_key_path, public_key_path, password=None):
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        self.password = password

    def _open(self, service):
        # RESOLUCCION 0004: pagina 756
        from zeep.wsse import utils

        client = zeep.Client(service.get_wsdl(), wsse=
                           [
                               BinarySignature(
                                   self.private_key_path, self.public_key_path, self.password,
                                   signature_method=xmlsec.Transform.RSA_SHA256,
                                   digest_method=xmlsec.Transform.SHA256)
                           ],
        )
        return client
    

