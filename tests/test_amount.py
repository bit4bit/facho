#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest

import facho.fe.form as form


def test_amount_positive():
    with pytest.raises(ValueError):
        form.Amount(-1.0)

def test_amount_equals():
    price1 = form.Amount(110.0)
    price2 = form.Amount(100 + 10.0)
    assert price1 == price2
    assert price1 == form.Amount(100) + form.Amount(10)
    assert price1 == form.Amount(10) * form.Amount(10) + form.Amount(10)
    assert form.Amount(110) == (form.Amount(1.10) * form.Amount(100))
    
def test_round():
    # Entre 0 y 5 Mantener el dígito menos significativo
    assert form.Amount(1.133).round(2) == form.Amount(1.13)
    # Entre 6 y 9 Incrementar el dígito menos significativo
    assert form.Amount(1.166).round(2) == form.Amount(1.17)
    # 5, y el segundo dígito siguiente al dígito menos significativo es cero o par Mantener el dígito menos significativo
    assert str(form.Amount(1.1560).round(2)) == str(form.Amount(1.15))
    # 5, y el segundo dígito siguiente al dígito menos significativo es impar Incrementar el dígito menos significativo
    assert form.Amount(1.1569).round(2) == form.Amount(1.157)

def test_amount_truncate():
    assert form.Amount(1.1569).truncate_as_string(2) == '1.15'
    assert form.Amount(587.0700).truncate_as_string(2) == '587.07'
    assert form.Amount(14705.8800).truncate_as_string(2) == '14705.88'
    assert form.Amount(9423.7000).truncate_as_string(2) == '9423.70'
    assert form.Amount(10084.03).truncate_as_string(2) == '10084.03'
    assert form.Amount(10000.02245).truncate_as_string(2) == '10000.02'
    assert form.Amount(10000.02357).truncate_as_string(2) == '10000.02'

def test_amount_format():
    assert str(round(form.Amount(1.1569),2)) == '1.16'
