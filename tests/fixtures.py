import pytest
import facho.fe.form as form
from datetime import datetime

@pytest.fixture
def simple_debit_note_without_lines():
    inv = form.DebitNote(form.InvoiceDocumentReference('1234', 'xx', datetime.now()))
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('ABC123')
    inv.set_operation_type('30')
    inv.set_payment_mean(form.PaymentMean(form.PaymentMean.DEBIT, '41', datetime.now(), '1234'))
    inv.set_supplier(form.Party(
        name = 'facho-supplier',
        ident = form.PartyIdentification('123','', '31'),
        responsability_code = form.Responsability(['O-07']),
        responsability_regime_code = '48',
        organization_code = '1',
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    inv.set_customer(form.Party(
        name = 'facho-customer',
        ident = form.PartyIdentification('321', '', '31'),
        responsability_code = form.Responsability(['O-07']),
        responsability_regime_code = '48',
        organization_code = '1',
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    return inv

@pytest.fixture
def simple_credit_note_without_lines():
    inv = form.CreditNote(form.InvoiceDocumentReference('1234', 'xx', datetime.now()))
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('ABC123')
    inv.set_operation_type('20')
    inv.set_payment_mean(form.PaymentMean(form.PaymentMean.DEBIT, '41', datetime.now(), '1234'))
    inv.set_supplier(form.Party(
        name = 'facho-supplier',
        ident = form.PartyIdentification('123','', '31'),
        responsability_code = form.Responsability(['O-07']),
        responsability_regime_code = '48',
        organization_code = '1',
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    inv.set_customer(form.Party(
        name = 'facho-customer',
        ident = form.PartyIdentification('321', '', '31'),
        responsability_code = form.Responsability(['O-07']),
        responsability_regime_code = '48',
        organization_code = '1',
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    return inv

@pytest.fixture
def simple_invoice_without_lines():
    inv = form.NationalSalesInvoice()
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('ABC123')
    inv.set_operation_type('10')
    inv.set_payment_mean(form.PaymentMean(form.PaymentMean.DEBIT, '41', datetime.now(), '1234'))
    inv.set_supplier(form.Party(
        name = 'facho-supplier',
        ident = form.PartyIdentification('123','', '31'),
        responsability_code = form.Responsability(['O-07']),
        responsability_regime_code = '48',
        organization_code = '1',
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    inv.set_customer(form.Party(
        name = 'facho-customer',
        ident = form.PartyIdentification('321', '', '31'),
        responsability_code = form.Responsability(['O-07']),
        responsability_regime_code = '48',
        organization_code = '1',
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    return inv

@pytest.fixture
def simple_invoice():
    inv = form.NationalSalesInvoice()
    inv.set_period(datetime.now(), datetime.now())
    inv.set_issue(datetime.now())
    inv.set_ident('ABC123')
    inv.set_operation_type('10')
    inv.set_payment_mean(form.PaymentMean(form.PaymentMean.DEBIT, '41', datetime.now(), ' 1234'))
    inv.set_supplier(form.Party(
        name = 'facho-supplier',
        ident = form.PartyIdentification('123','', '31'),
        responsability_code = form.Responsability(['O-07']),
        responsability_regime_code = '48',
        organization_code = '1',
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    inv.set_customer(form.Party(
        name = 'facho-customer',
        ident = form.PartyIdentification('321','', '31'),
        responsability_code = form.Responsability(['O-07']),
        responsability_regime_code = '48',
        organization_code = '1',
        address = form.Address(
            '', '', form.City('05001', 'Medellín'),
            form.Country('CO', 'Colombia'),
            form.CountrySubentity('05', 'Antioquia'))
    ))
    inv.add_invoice_line(form.InvoiceLine(
        quantity = form.Quantity(1, '94'),
        description = 'producto facho',
        item = form.StandardItem( 9999),
        price = form.Price(form.Amount(100.0), '01', ''),
        tax = form.TaxTotal(
            tax_amount = form.Amount(0.0),
            taxable_amount = form.Amount(0.0),
            subtotals = [
                form.TaxSubTotal(
                    percent = 19.0,
                )
            ]
        )
    ))
    return inv
