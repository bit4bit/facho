from .. import fe
from ..form import *

__all__ = ['DIANCreditNoteXML']

class DIANCreditNoteXML(fe.FeXML):
    """
    DianInvoiceXML mapea objeto form.Invoice a XML segun
    lo indicado para la facturacion electronica.
    """

    def __init__(self, invoice):
        super().__init__('CreditNote', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')
        self.placeholder_for('/fe:CreditNote/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')

        # ZE02 se requiere existencia para firmar
        ublextension = self.fragment('/fe:CreditNote/ext:UBLExtensions/ext:UBLExtension', append=True)
        extcontent = ublextension.find_or_create_element('/ext:UBLExtension/ext:ExtensionContent')
        self.attach_invoice(invoice)
 
    def set_supplier(fexml, invoice):
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingSupplierParty')
        #DIAN 1.7.-2020: CAJ02
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cbc:AdditionalAccountID',
                          invoice.invoice_supplier.organization_code)
        #DIAN 1.7.-2020: CAJ06
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_supplier.name)
        #DIAN 1.7.-2020: CAJ07, CAJ08
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address')
        #DIAN 1.7.-2020: CAJ09
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: CAJ10
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName',
                          invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: CAJ11
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)
        #DIAN 1.7.-2020: CAJ12
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: CAJ13, CAJ14
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)
        #DIAN 1.7.-2020: CAJ16, CAJ16
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)
        #DIAN 1.7.-2020: CAJ17
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                         #DIAN 1.7.-2020: CAJ18
                          languageID='es')

        supplier_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        supplier_company_id_attrs.update({'schemeID': invoice.invoice_supplier.ident.dv,
                                          'schemeName': invoice.invoice_supplier.ident.type_fiscal})

        #DIAN 1.7.-2020: CAJ19
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme')
        #DIAN 1.7.-2020: CAJ20
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        #DIAN 1.7.-2020: CAJ21
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          #DIAN 1.7.-2020: CAJ22,CAJ23,CAJ24,CAJ25
                          **supplier_company_id_attrs)
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          #DIAN 1.7.-2020: CAJ26
                          invoice.invoice_supplier.responsability_code,
                          #DIAN 1.7.-2020: CAJ27
                          listName=invoice.invoice_supplier.responsability_regime_code)
        #DIAN 1.7.-2020: CAJ28
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')
        #DIAN 1.7.-2020: CAJ29
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: CAJ30
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName', invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: CAJ31
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)
        #DIAN 1.7.-2020: CAJ32
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: CAJ33,CAJ34
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)
        #DIAN 1.7.-2020: CAJ35,CAJ36
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)
        #DIAN 1.7.-2020: CAJ37,CAJ38
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                          languageID='es')
        #DIAN 1.7.-2020: CAJ39
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')
        #DIAN 1.7.-2020: CAJ40
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          invoice.invoice_customer.tax_scheme.code)
        #DIAN 1.7.-2020: CAJ41
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          invoice.invoice_customer.tax_scheme.name)                          
        #DIAN 1.7.-2020: CAJ42
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: CAJ43
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        #DIAN 1.7.-2020: CAJ44,CAJ45,CAJ46,CAJ47,CAJ48
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          **supplier_company_id_attrs)
        #DIAN 1.7.-2020: CAJ49
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme')
        #DIAN 1.7.-2020: CAJ50
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme/cbc:ID',
                          'SETP')
        #DIAN 1.7.-2020: CAJ67
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:Contact')
        #DIAN 1.7.-2020: CAJ71
        fexml.set_element('/fe:CreditNote/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_supplier.email)


    def set_customer(fexml, invoice):
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty')
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cbc:AdditionalAccountID',
                          invoice.invoice_customer.organization_code)
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID',
                          invoice.invoice_customer.ident)
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_customer.name)

        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation')
        customer_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        #DIAN 1.7.-2020: CAK25
        customer_company_id_attrs.update({'schemeID': invoice.invoice_customer.ident.dv,
                                          'schemeName': invoice.invoice_customer.ident.type_fiscal})
        #DIAN 1.7.-2020: CAK07
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address')
        #DIAN 1.7.-2020: CAK08
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: CAK09
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName', invoice.invoice_customer.address.city.name)
        #DIAN 1.7.-2020: CAK11
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)
        #DIAN 1.7.-2020: CAK12
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)
        #DIAN 1.7.-2020: CAK13, CAK14
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)
        #DIAN 1.7.-2020: CAK16
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)
        #DIAN 1.7.-2020: CAK17
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_customer.address.country.name,
                         #DIAN 1.7.-2020: CAK18
                          languageID='es')
        #DIAN 1.7.-2020: CAK19
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme')
        #DIAN 1.7.-2020: CAK20
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        #DIAN 1.7.-2020: CAK21
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          #DIAN 1.7.-2020: CAK22, CAK23, CAK24, CAK25
                          **customer_company_id_attrs)
        #DIAN 1.7.-2020: CAK26
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          invoice.invoice_customer.responsability_code,
                          #DIAN 1.7.-2020: CAK27
                          listName=invoice.invoice_customer.responsability_regime_code)
        #DIAN 1.7.-2020: CAK28
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')
        #DIAN 1.7.-2020: CAK29
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: CAK30
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName',
                          invoice.invoice_customer.address.city.name)
        #DIAN 1.7.-2020: CAK31
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)
        #DIAN 1.7.-2020: CAK32
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)
        #DIAN 1.7.-2020: CAK33
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine')
        #DIAN 1.7.-2020: CAK34
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)
        #DIAN 1.7.-2020: CAK35
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country')
        #DIAN 1.7.-2020: CAK36
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)
        #DIAN 1.7.-2020: CAK37
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name', invoice.invoice_customer.address.country.name)
        #DIAN 1.7.-2020: CAK38
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code,
                          languageID='es')
        #DIAN 1.7.-2020: CAK39
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')
        #DIAN 1.7.-2020: CAK40 Machete Construir Validación
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          invoice.invoice_customer.tax_scheme.code)
        #DIAN 1.7.-2020: CAK41 Machete Construir Validación
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          invoice.invoice_customer.tax_scheme.name)
        #DIAN 1.7.-2020: CAK42
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: CAK43
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        #DIAN 1.7.-2020: CAK44
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          #DIAN 1.7.-2020: CAK45, CAK46, CAK47, CAK48
                          **customer_company_id_attrs)
        #DIAN 1.7.-2020: CAK51
        fexml.placeholder_for('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: CAK51, CAK55
        fexml.set_element('/fe:CreditNote/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_customer.email)
        
        
    def set_payment_mean(fexml, invoice):
        payment_mean = invoice.invoice_payment_mean
        fexml.set_element('/fe:CreditNote/cac:PaymentMeans/cbc:ID', payment_mean.id)
        fexml.set_element('/fe:CreditNote/cac:PaymentMeans/cbc:PaymentMeansCode', payment_mean.code)
        fexml.set_element('/fe:CreditNote/cac:PaymentMeans/cbc:PaymentDueDate', payment_mean.due_at.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:CreditNote/cac:PaymentMeans/cbc:PaymentID', payment_mean.payment_id)

    def set_element_amount_for(fexml, xml, xpath, amount):
        if not isinstance(amount, Amount):
            raise TypeError("amount not is Amount")

        xml.set_element(xpath, amount, currencyID=amount.currency.code)

    def set_element_amount(fexml, xpath, amount):
        if not isinstance(amount, Amount):
            raise TypeError("amount not is Amount")

        fexml.set_element(xpath, amount, currencyID=amount.currency.code)

    def set_legal_monetary(fexml, invoice):
        fexml.set_element_amount('/fe:CreditNote/cac:LegalMonetaryTotal/cbc:LineExtensionAmount',
                                 invoice.invoice_legal_monetary_total.line_extension_amount)

        fexml.set_element_amount('/fe:CreditNote/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_exclusive_amount)

        fexml.set_element_amount('/fe:CreditNote/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_inclusive_amount)

        fexml.set_element_amount('/fe:CreditNote/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount',
                                invoice.invoice_legal_monetary_total.charge_total_amount)

        fexml.set_element_amount('/fe:CreditNote/cac:LegalMonetaryTotal/cbc:PayableAmount',
                                invoice.invoice_legal_monetary_total.payable_amount)

    def set_billing_reference(fexml, invoice):
        fexml.placeholder_for('/fe:CreditNote/cac:BillingReference')
        fexml.placeholder_for('/fe:CreditNote/cac:BillingReference/cac:InvoiceDocumentReference')
        fexml.set_element('/fe:CreditNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID',
                                invoice.invoice_bill_reference_ident)
        fexml.set_element('/fe:CreditNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:UUID',
                                invoice.invoice_bill_reference_uuid,
                                schemeName='CUFE-SHA384')
        fexml.set_element('/fe:CreditNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:IssueDate',
                                invoice.invoice_bill_reference_date)
        
    def set_invoice_totals(fexml, invoice):
        tax_amount_for = defaultdict(lambda: defaultdict(lambda: 0.0))
        percent_for = defaultdict(lambda: None)

        #requeridos para CUFE
        tax_amount_for['01']['tax_amount'] = Amount(0.0)
        tax_amount_for['01']['taxable_amount'] = Amount(0.0)
        #DIAN 1.7.-2020: FAS07 => Se debe construir estrategia para  su manejo
        #tax_amount_for['04']['tax_amount'] = 0.0
        #tax_amount_for['04']['taxable_amount'] = 0.0
        #tax_amount_for['03']['tax_amount'] = 0.0
        #tax_amount_for['03']['taxable_amount'] = 0.0

        total_tax_amount = Amount(0.0)

        for invoice_line in invoice.invoice_lines:
            for subtotal in invoice_line.tax.subtotals:
                tax_amount_for[subtotal.tax_scheme_ident]['tax_amount'] += subtotal.tax_amount
                tax_amount_for[subtotal.tax_scheme_ident]['taxable_amount'] += subtotal.taxable_amount
                total_tax_amount += subtotal.tax_amount
                # MACHETE ojo CreditNoteLine.tax pasar a CreditNote
                percent_for[subtotal.tax_scheme_ident] = subtotal.percent

        fexml.placeholder_for('/fe:CreditNote/cac:TaxTotal')
        fexml.set_element_amount('/fe:CreditNote/cac:TaxTotal/cbc:TaxAmount',
                                total_tax_amount)


        for index, item in enumerate(tax_amount_for.items()):
            cod_impuesto, amount_of = item
            next_append = index > 0

            #DIAN 1.7.-2020: FAS01
            line = fexml.fragment('/fe:CreditNote/cac:TaxTotal', append=next_append)

            #DIAN 1.7.-2020: FAU06
            tax_amount = amount_of['tax_amount']
            fexml.set_element_amount_for(line,
                                         '/cac:TaxTotal/cbc:TaxAmount',
                                         tax_amount)

            #DIAN 1.7.-2020: FAS05
            fexml.set_element_amount_for(line,
                                         '/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount',
                                         amount_of['taxable_amount'])

            #DIAN 1.7.-2020: FAU06
            fexml.set_element_amount_for(line,
                                         '/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount',
                                         amount_of['tax_amount'])

            #DIAN 1.7.-2020: FAS07
            if percent_for[cod_impuesto]:
                line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cbc:Percent',
                                 percent_for[cod_impuesto])


            if percent_for[cod_impuesto]:
                line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent',
                                 percent_for[cod_impuesto])
            line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID',
                             cod_impuesto)


    def set_invoice_lines(fexml, invoice):
        next_append = False
        for index, invoice_line in enumerate(invoice.invoice_lines):
            line = fexml.fragment('/fe:CreditNote/cac:CreditNoteLine', append=next_append)
            next_append = True

            line.set_element('/cac:CreditNoteLine/cbc:ID', index + 1)
            line.set_element('/cac:CreditNoteLine/cbc:CreditedQuantity', invoice_line.quantity, unitCode = 'NAR')
            fexml.set_element_amount_for(line,
                                         '/cac:CreditNoteLine/cbc:LineExtensionAmount',
                                         invoice_line.total_amount)
            fexml.set_element_amount_for(line,
                                         '/cac:CreditNoteLine/cac:TaxTotal/cbc:TaxAmount',
                                         invoice_line.tax_amount)


            for subtotal in invoice_line.tax.subtotals:
                fexml.set_element_amount_for(line,
                                             '/cac:CreditNoteLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount',
                                             subtotal.taxable_amount)
                line.set_element('/cac:CreditNoteLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount', subtotal.tax_amount, currencyID='COP')
                line.set_element('/cac:CreditNoteLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent', subtotal.percent)
                line.set_element('/cac:CreditNoteLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID', subtotal.tax_scheme_ident)
                line.set_element('/cac:CreditNoteLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name', subtotal.tax_scheme_name)
            line.set_element('/cac:CreditNoteLine/cac:Item/cbc:Description', invoice_line.item.description)
            # TODO
            line.set_element('/cac:CreditNoteLine/cac:Item/cac:StandardItemIdentification/cbc:ID', invoice_line.item.id)
            line.set_element('/cac:CreditNoteLine/cac:Price/cbc:PriceAmount', invoice_line.price.amount, currencyID="COP")
            #DIAN 1.7.-2020: FBB04
            line.set_element('/cac:CreditNoteLine/cac:Price/cbc:BaseQuantity', invoice_line.price.amount)

    def attach_invoice(fexml, invoice):
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""

        fexml.placeholder_for('/fe:CreditNote/ext:UBLExtensions')
        fexml.set_element('/fe:CreditNote/cbc:UBLVersionID', 'UBL 2.1')
        fexml.set_element('/fe:CreditNote/cbc:CustomizationID', invoice.invoice_operation_type)
        fexml.placeholder_for('/fe:CreditNote/cbc:ProfileID')
        fexml.placeholder_for('/fe:CreditNote/cbc:ProfileExecutionID')
        fexml.set_element('/fe:CreditNote/cbc:ID', invoice.invoice_ident)
        fexml.placeholder_for('/fe:CreditNote/cbc:UUID')
        fexml.set_element('/fe:CreditNote/cbc:DocumentCurrencyCode', 'COP')
        fexml.set_element('/fe:CreditNote/cbc:IssueDate', invoice.invoice_issue.strftime('%Y-%m-%d'))
        #DIAN 1.7.-2020: FAD10
        fexml.set_element('/fe:CreditNote/cbc:IssueTime', invoice.invoice_issue.strftime('%H:%M:%S-05:00'))
        fexml.set_billing_reference(invoice)
        fexml.set_element('/fe:CreditNote/cbc:CreditNoteTypeCode', codelist.TipoDocumento.by_name('Nota Crédito')['code'],
                          listAgencyID='195',
                          listAgencyName='No matching global declaration available for the validation root',
                          listURI='http://www.dian.gov.co')
        fexml.set_element('/fe:CreditNote/cbc:LineCountNumeric', len(invoice.invoice_lines))
        fexml.set_element('/fe:CreditNote/cac:CreditNotePeriod/cbc:StartDate', invoice.invoice_period_start.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:CreditNote/cac:CreditNotePeriod/cbc:EndDate', invoice.invoice_period_end.strftime('%Y-%m-%d'))

        fexml.set_supplier(invoice)
        fexml.set_customer(invoice)
        fexml.set_invoice_totals(invoice)
        fexml.set_legal_monetary(invoice)
        fexml.set_invoice_lines(invoice)
        fexml.set_payment_mean(invoice)

        return fexml
