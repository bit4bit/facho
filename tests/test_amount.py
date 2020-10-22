#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of facho.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Tests for `facho` package."""

import pytest

import facho.fe.form as form


def test_amount_equals():
    price1 = form.Amount(110.0)
    price2 = form.Amount(100 + 10.0)
    assert price1 == price2
    assert price1 == form.Amount(100) + form.Amount(10)
    assert price1 == form.Amount(10) * form.Amount(10) + form.Amount(10)
