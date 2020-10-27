from .. import fe
from ..form import *

__all__ = ['DIANDebitNoteXML']

class DIANDebitNoteXML(fe.FeXML):
    """
    DianInvoiceXML mapea objeto form.Invoice a XML segun
    lo indicado para la facturacion electronica.
    """

    def __init__(self, invoice):
        super().__init__('DebitNote', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')
        self.placeholder_for('/fe:DebitNote/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')

        # ZE02 se requiere existencia para firmar
        ublextension = self.fragment('/fe:DebitNote/ext:UBLExtensions/ext:UBLExtension', append=True)
        extcontent = ublextension.find_or_create_element('/ext:UBLExtension/ext:ExtensionContent')
        self.attach_invoice(invoice)
 
    def set_supplier(fexml, invoice):
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingSupplierParty')
        #DIAN 1.7.-2020: DAJ02
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cbc:AdditionalAccountID',
                          invoice.invoice_supplier.organization_code)
        #DIAN 1.7.-2020: DAJ06
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_supplier.name)
        #DIAN 1.7.-2020: DAJ07, DAJ08
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address')
        #DIAN 1.7.-2020: DAJ09
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: DAJ10
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName',
                          invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: DAJ11
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)
        #DIAN 1.7.-2020: DAJ12
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: DAJ13, DAJ14
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)
        #DIAN 1.7.-2020: DAJ16, DAJ16
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)
        #DIAN 1.7.-2020: DAJ17
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                         #DIAN 1.7.-2020: DAJ18
                          languageID='es')

        supplier_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        supplier_company_id_attrs.update({'schemeID': invoice.invoice_supplier.ident.dv,
                                          'schemeName': invoice.invoice_supplier.ident.type_fiscal})

        #DIAN 1.7.-2020: DAJ19
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme')
        #DIAN 1.7.-2020: DAJ20
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        #DIAN 1.7.-2020: DAJ21
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          #DIAN 1.7.-2020: DAJ22,DAJ23,DAJ24,DAJ25
                          **supplier_company_id_attrs)
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          #DIAN 1.7.-2020: DAJ26
                          invoice.invoice_supplier.responsability_code,
                          #DIAN 1.7.-2020: DAJ27
                          listName=invoice.invoice_supplier.responsability_regime_code)
        #DIAN 1.7.-2020: DAJ28
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')
        #DIAN 1.7.-2020: DAJ29
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: DAJ30
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName', invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: DAJ31
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)
        #DIAN 1.7.-2020: DAJ32
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: DAJ33,DAJ34
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)
        #DIAN 1.7.-2020: DAJ35,DAJ36
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)
        #DIAN 1.7.-2020: DAJ37,DAJ38
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                          languageID='es')
        #DIAN 1.7.-2020: DAJ39
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')
        #DIAN 1.7.-2020: DAJ40
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          invoice.invoice_customer.tax_scheme.code)
        #DIAN 1.7.-2020: DAJ41
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          invoice.invoice_customer.tax_scheme.name)                          
        #DIAN 1.7.-2020: DAJ42
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: DAJ43
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        #DIAN 1.7.-2020: DAJ44,DAJ45,DAJ46,DAJ47,DAJ48
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          **supplier_company_id_attrs)
        #DIAN 1.7.-2020: DAJ49
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme')
        #DIAN 1.7.-2020: DAJ50
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme/cbc:ID',
                          'SETP')
        #DIAN 1.7.-2020: DAJ67
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:Contact')
        #DIAN 1.7.-2020: DAJ71
        fexml.set_element('/fe:DebitNote/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_supplier.email)


    def set_customer(fexml, invoice):
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty')
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cbc:AdditionalAccountID',
                          invoice.invoice_customer.organization_code)
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID',
                          invoice.invoice_customer.ident)
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_customer.name)

        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation')
        customer_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        #DIAN 1.7.-2020: DAK25
        customer_company_id_attrs.update({'schemeID': invoice.invoice_customer.ident.dv,
                                          'schemeName': invoice.invoice_customer.ident.type_fiscal})
        #DIAN 1.7.-2020: DAK07
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address')
        #DIAN 1.7.-2020: DAK08
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: DAK09
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName', invoice.invoice_customer.address.city.name)
        #DIAN 1.7.-2020: DAK11
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)
        #DIAN 1.7.-2020: DAK12
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)
        #DIAN 1.7.-2020: DAK13, DAK14
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)
        #DIAN 1.7.-2020: DAK16
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)
        #DIAN 1.7.-2020: DAK17
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_customer.address.country.name,
                         #DIAN 1.7.-2020: DAK18
                          languageID='es')
        #DIAN 1.7.-2020: DAK19
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme')
        #DIAN 1.7.-2020: DAK20
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        #DIAN 1.7.-2020: DAK21
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          #DIAN 1.7.-2020: DAK22, DAK23, DAK24, DAK25
                          **customer_company_id_attrs)
        #DIAN 1.7.-2020: DAK26
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          invoice.invoice_customer.responsability_code,
                          #DIAN 1.7.-2020: DAK27
                          listName=invoice.invoice_customer.responsability_regime_code)
        #DIAN 1.7.-2020: DAK28
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')
        #DIAN 1.7.-2020: DAK29
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: DAK30
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName',
                          invoice.invoice_customer.address.city.name)
        #DIAN 1.7.-2020: DAK31
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)
        #DIAN 1.7.-2020: DAK32
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)
        #DIAN 1.7.-2020: DAK33
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine')
        #DIAN 1.7.-2020: DAK34
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)
        #DIAN 1.7.-2020: DAK35
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country')
        #DIAN 1.7.-2020: DAK36
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)
        #DIAN 1.7.-2020: DAK37
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name', invoice.invoice_customer.address.country.name)
        #DIAN 1.7.-2020: DAK38
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code,
                          languageID='es')
        #DIAN 1.7.-2020: DAK39
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')
        #DIAN 1.7.-2020: DAK40 Machete Construir Validación
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          invoice.invoice_customer.tax_scheme.code)
        #DIAN 1.7.-2020: DAK41 Machete Construir Validación
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          invoice.invoice_customer.tax_scheme.name)
        #DIAN 1.7.-2020: DAK42
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: DAK43
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        #DIAN 1.7.-2020: DAK44
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          #DIAN 1.7.-2020: DAK45, DAK46, DAK47, DAK48
                          **customer_company_id_attrs)
        #DIAN 1.7.-2020: CAK51
        fexml.placeholder_for('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: CAK51, CAK55
        fexml.set_element('/fe:DebitNote/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_customer.email)
        

    def set_payment_mean(fexml, invoice):
        payment_mean = invoice.invoice_payment_mean
        fexml.set_element('/fe:DebitNote/cac:PaymentMeans/cbc:ID', payment_mean.id)
        fexml.set_element('/fe:DebitNote/cac:PaymentMeans/cbc:PaymentMeansCode', payment_mean.code)
        fexml.set_element('/fe:DebitNote/cac:PaymentMeans/cbc:PaymentDueDate', payment_mean.due_at.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:DebitNote/cac:PaymentMeans/cbc:PaymentID', payment_mean.payment_id)

    def set_element_amount_for(fexml, xml, xpath, amount):
        if not isinstance(amount, Amount):
            raise TypeError("amount not is Amount")

        xml.set_element(xpath, amount, currencyID=amount.currency.code)

    def set_element_amount(fexml, xpath, amount):
        if not isinstance(amount, Amount):
            raise TypeError("amount not is Amount")

        fexml.set_element(xpath, amount, currencyID=amount.currency.code)

    def set_legal_monetary(fexml, invoice):
        fexml.set_element_amount('/fe:DebitNote/cac:LegalMonetaryTotal/cbc:LineExtensionAmount',
                                 invoice.invoice_legal_monetary_total.line_extension_amount)

        fexml.set_element_amount('/fe:DebitNote/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_exclusive_amount)

        fexml.set_element_amount('/fe:DebitNote/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_inclusive_amount)

        fexml.set_element_amount('/fe:DebitNote/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount',
                                invoice.invoice_legal_monetary_total.charge_total_amount)

        fexml.set_element_amount('/fe:DebitNote/cac:LegalMonetaryTotal/cbc:PayableAmount',
                                invoice.invoice_legal_monetary_total.payable_amount)
    def set_billing_reference(fexml, invoice):
        fexml.placeholder_for('/fe:DebitNote/cac:BillingReference')
        fexml.placeholder_for('/fe:DebitNote/cac:BillingReference/cac:InvoiceDocumentReference')
        fexml.set_element('/fe:DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID',
                                invoice.invoice_billing_reference.ident)
        fexml.set_element('/fe:DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:UUID',
                                invoice.invoice_billing_reference.uuid,
                                schemeName='CUFE-SHA384')
        fexml.set_element('/fe:DebitNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:IssueDate',
                                invoice.invoice_billing_reference.date)
        
        
    def set_invoice_totals(fexml, invoice):
        tax_amount_for = defaultdict(lambda: defaultdict(lambda: 0.0))
        percent_for = defaultdict(lambda: None)

        #requeridos para CUDE
        tax_amount_for['01']['tax_amount'] = Amount(0.0)
        tax_amount_for['01']['taxable_amount'] = Amount(0.0)
        #DIAN 1.7.-2020: DAS07 => Se debe construir estrategia para  su manejo
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
                # MACHETE ojo DebitNoteLine.tax pasar a DebitNote
                percent_for[subtotal.tax_scheme_ident] = subtotal.percent

        fexml.placeholder_for('/fe:DebitNote/cac:TaxTotal')
        fexml.set_element_amount('/fe:DebitNote/cac:TaxTotal/cbc:TaxAmount',
                                total_tax_amount)


        for index, item in enumerate(tax_amount_for.items()):
            cod_impuesto, amount_of = item
            next_append = index > 0

            #DIAN 1.7.-2020: DAS01
            line = fexml.fragment('/fe:DebitNote/cac:TaxTotal', append=next_append)

            #DIAN 1.7.-2020: DAU06
            tax_amount = amount_of['tax_amount']
            fexml.set_element_amount_for(line,
                                         '/cac:TaxTotal/cbc:TaxAmount',
                                         tax_amount)

            #DIAN 1.7.-2020: DAS05
            fexml.set_element_amount_for(line,
                                         '/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount',
                                         amount_of['taxable_amount'])

            #DIAN 1.7.-2020: DAU06
            fexml.set_element_amount_for(line,
                                         '/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount',
                                         amount_of['tax_amount'])

            #DIAN 1.7.-2020: DAS07
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
            line = fexml.fragment('/fe:DebitNote/cac:DebitNoteLine', append=next_append)
            next_append = True

            line.set_element('/cac:DebitNoteLine/cbc:ID', index + 1)
            line.set_element('/cac:DebitNoteLine/cbc:DebitedQuantity', invoice_line.quantity, unitCode = 'NAR')
            fexml.set_element_amount_for(line,
                                         '/cac:DebitNoteLine/cbc:LineExtensionAmount',
                                         invoice_line.total_amount)
            fexml.set_element_amount_for(line,
                                         '/cac:DebitNoteLine/cac:TaxTotal/cbc:TaxAmount',
                                         invoice_line.tax_amount)


            for subtotal in invoice_line.tax.subtotals:
                fexml.set_element_amount_for(line,
                                             '/cac:DebitNoteLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount',
                                             subtotal.taxable_amount)
                line.set_element('/cac:DebitNoteLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount', subtotal.tax_amount, currencyID='COP')
                line.set_element('/cac:DebitNoteLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent', subtotal.percent)
                line.set_element('/cac:DebitNoteLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID', subtotal.tax_scheme_ident)
                line.set_element('/cac:DebitNoteLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name', subtotal.tax_scheme_name)
            line.set_element('/cac:DebitNoteLine/cac:Item/cbc:Description', invoice_line.item.description)
            # TODO
            line.set_element('/cac:DebitNoteLine/cac:Item/cac:StandardItemIdentification/cbc:ID', invoice_line.item.id)
            line.set_element('/cac:DebitNoteLine/cac:Price/cbc:PriceAmount', invoice_line.price.amount, currencyID="COP")
            #DIAN 1.7.-2020: DBB04
            line.set_element('/cac:DebitNoteLine/cac:Price/cbc:BaseQuantity', invoice_line.price.amount)

    def attach_invoice(fexml, invoice):
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""

        fexml.placeholder_for('/fe:DebitNote/ext:UBLExtensions')
        fexml.set_element('/fe:DebitNote/cbc:UBLVersionID', 'UBL 2.1')
        fexml.set_element('/fe:DebitNote/cbc:CustomizationID', invoice.invoice_operation_type)
        fexml.placeholder_for('/fe:DebitNote/cbc:ProfileID')
        fexml.placeholder_for('/fe:DebitNote/cbc:ProfileExecutionID')
        fexml.set_element('/fe:DebitNote/cbc:ID', invoice.invoice_ident)
        fexml.placeholder_for('/fe:DebitNote/cbc:UUID')
        fexml.set_element('/fe:DebitNote/cbc:DocumentCurrencyCode', 'COP')
        fexml.set_element('/fe:DebitNote/cbc:IssueDate', invoice.invoice_issue.strftime('%Y-%m-%d'))
        #DIAN 1.7.-2020: DAD10
        fexml.set_element('/fe:DebitNote/cbc:IssueTime', invoice.invoice_issue.strftime('%H:%M:%S-05:00'))
        fexml.set_billing_reference(invoice)
        fexml.set_element('/fe:DebitNote/cbc:DebitNoteTypeCode', codelist.TipoDocumento.by_name('Nota Crédito')['code'],
                          listAgencyID='195',
                          listAgencyName='No matching global declaration available for the validation root',
                          listURI='http://www.dian.gov.co')
        fexml.set_element('/fe:DebitNote/cbc:LineCountNumeric', len(invoice.invoice_lines))
        fexml.set_element('/fe:DebitNote/cac:DebitNotePeriod/cbc:StartDate', invoice.invoice_period_start.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:DebitNote/cac:DebitNotePeriod/cbc:EndDate', invoice.invoice_period_end.strftime('%Y-%m-%d'))

        fexml.set_supplier(invoice)
        fexml.set_customer(invoice)
        fexml.set_invoice_totals(invoice)
        fexml.set_legal_monetary(invoice)
        fexml.set_invoice_lines(invoice)
        fexml.set_payment_mean(invoice)

        return fexml
