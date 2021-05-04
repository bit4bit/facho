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
class GetNumberingRangeResponse:

    @dataclass
    class NumberRangeResponse:
        ResolutionNumber: str
        ResolutionDate: str
        Prefix: str
        FromNumber: int
        ToNumber: int
        ValidateDateFrom: str
        ValidateDateTo: str
        TechnicalKey: str

    NumberRangeResponse: List[NumberRangeResponse]


    @classmethod
    def fromdict(cls, data):
        return cls(
            data['NumberRangeResponse']
        )


@dataclass
class GetNumberingRange(SOAPService):
    accountCode: str
    accountCodeT: str
    softwareCode: str

    def get_wsdl(self):
        return 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'GetNumberingRange'

    def build_response(self, as_dict):
        return GetNumberingRangeResponse.fromdict(as_dict)


@dataclass
class SendBillAsync(SOAPService):
    fileName: str
    contentFile: str

    def get_wsdl(self):
        return 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'SendBillAsync'

    def build_response(self, as_dict):
        return as_dict


@dataclass
class SendTestSetAsyncResponse:
    ZipKey: str
    ErrorMessageList: List[str]

    @classmethod
    def fromdict(cls, data):
        return cls(
            data['ZipKey'],
            data['ErrorMessageList'] or []
        )

@dataclass
class SendTestSetAsync(SOAPService):
    fileName: str
    contentFile: str
    testSetId: str = ''

    def get_wsdl(self):
        return 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'SendTestSetAsync'

    def build_response(self, as_dict):
        return SendTestSetAsyncResponse.fromdict(as_dict)

@dataclass
class SendBillSync(SOAPService):
    fileName: str
    contentFile: bytes

    def get_wsdl(self):
        return 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'SendBillSync'

    def build_response(self, as_dict):
        return as_dict

@dataclass
class GetStatusResponse:
    IsValid: bool
    StatusDescription: str
    StatusCode: int
    ErrorMessage: List[str]

    @classmethod
    def fromdict(cls, data):
        if data['ErrorMessage']:
            error_message = data['ErrorMessage']['string']
        else:
            error_message = None
            
        return cls(data['IsValid'],
                   data['StatusDescription'],
                   data['StatusCode'],
                   error_message)
                   

@dataclass
class GetStatus(SOAPService):
    trackId: bytes

    def get_wsdl(self):
        return 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'GetStatus'

    def build_response(self, as_dict):
        return GetStatusResponse.fromdict(as_dict)

@dataclass
class GetStatusZip(SOAPService):
    trackId: bytes

    def get_wsdl(self):
        return 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'

    def get_service(self):
        return 'GetStatusZip'

    def build_response(self, as_dict):
        return GetStatusResponse.fromdict(as_dict[0])


class Habilitacion:
    WSDL = 'https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc?wsdl'

    class GetNumberingRange(GetNumberingRange):
        def get_wsdl(self):
            return Habilitacion.WSDL

    class SendBillAsync(SendBillAsync):
        def get_wsdl(self):
            return Habilitacion.WSDL

    class SendBillSync(SendBillSync):
        def get_wsdl(self):
            return Habilitacion.WSDL

    class SendTestSetAsync(SendTestSetAsync):
        def get_wsdl(self):
            return Habilitacion.WSDL

    class GetStatus(GetStatus):
        def get_wsdl(self):
            return Habilitacion.WSDL

    class GetStatusZip(GetStatusZip):
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
                             BinarySignature(
                                 self.private_key_path, self.public_key_path, self.password,
                                 signature_method=xmlsec.Transform.RSA_SHA256,
                                 digest_method=xmlsec.Transform.SHA256)
                             ,
        )
        return client
