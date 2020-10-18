#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from facho.fe.client import dian
from facho import facho

import pytest


from datetime import datetime

class FakeDianClient(dian.DianClient):
    def __init__(self, username, password, resp):
        super().__init__(username, password)
        self.response = resp

    def _open(self, service):
        return None

    def _close(self, conn):
        pass

    def _remote_service(self, conn, service):
        def fake_remote(**kw):
            return self.response
        return fake_remote


def test_sopa_consultaresolucionesfacturacion():
    expected_resp = {
        'NumberRangeResponse': [['test1', '', 'test', 0, 10, '', '', 'abc']]
    }

    client_dian = FakeDianClient('user', 'pass', expected_resp)
    resp = client_dian.request(dian.GetNumberingRange(
        '860046645', '800037646', '13a6a789-47ca-4728-adb8-372fca76e692'
    ))
    assert len(resp.NumberRangeResponse) == 1
