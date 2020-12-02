from .. import fe
from ..form import *

__all__ = ['DIANInvoiceXML']

class DIANInvoiceXML(fe.FeXML):
    """
    DianInvoiceXML mapea objeto form.Invoice a XML segun
    lo indicado para la facturacion electronica.
    """

    def __init__(self, invoice, tag_document = 'Invoice'):
        super().__init__(tag_document, 'http://www.dian.gov.co/contratos/facturaelectronica/v1')
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceControl')
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceSource')
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareProvider')
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareSecurityCode')
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:AuthorizationProvider/sts:AuthorizationProviderID')
        
        # ZE02 se requiere existencia para firmar
        ublextension = self.fragment('./ext:UBLExtensions/ext:UBLExtension', append=True)
        extcontent = ublextension.find_or_create_element('/ext:UBLExtension/ext:ExtensionContent')
        self.attach_invoice(invoice)

    def set_supplier(fexml, invoice):
        fexml.placeholder_for('./cac:AccountingSupplierParty')

        #DIAN 1.7.-2020: CAJ02
        #DIAN 1.7.-2020: FAJ02
        fexml.set_element('./cac:AccountingSupplierParty/cbc:AdditionalAccountID',
                          invoice.invoice_supplier.organization_code)

        #DIAN 1.7.-2020: CAJ06
        #DIAN 1.7.-2020: FAJ06
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_supplier.name)

        #DIAN 1.7.-2020: CAJ07, CAJ08
        #DIAN 1.7.-2020: FAJ07
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address')

        #DIAN 1.7.-2020: FAJ08
        #DIAN 1.7.-2020: CAJ09
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: FAJ09
        #DIAN 1.7.-2020: CAJ10
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName',
                          invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: FAJ11
        #DIAN 1.7.-2020: CAJ11
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)

        #DIAN 1.7.-2020: FAJ12
        #DIAN 1.7.-2020: CAJ12
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: FAJ14
        #DIAN 1.7.-2020: CAJ13, CAJ14
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)

        #DIAN 1.7.-2020: FAJ16
        #DIAN 1.7.-2020: CAJ16, CAJ16
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)

        #DIAN 1.7.-2020: FAJ17
        #DIAN 1.7.-2020: CAJ17
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                          #DIAN 1.7.-2020: FAJ18
                          languageID = 'es')

        supplier_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        supplier_company_id_attrs.update({'schemeID': invoice.invoice_supplier.ident.dv,
                                          'schemeName': invoice.invoice_supplier.ident.type_fiscal})

        #DIAN 1.7.-2020: FAJ19
        #DIAN 1.7.-2020: CAJ19
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme')

        #DIAN 1.7.-2020: FAJ20
        #DIAN 1.7.-2020: CAJ20
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)

        #DIAN 1.7.-2020: FAJ21
        #DIAN 1.7.-2020: CAJ21
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          #DIAN 1.7.-2020: FAJ22,FAJ23,FAJ24,FAJ25
                          **supplier_company_id_attrs)
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          #DIAN 1.7.-2020: FAJ26
                          #DIAN 1.7.-2020: CAJ26
                          invoice.invoice_supplier.responsability_code,
                          #DIAN 1.7.-2020: FAJ27
                          #DIAN 1.7.-2020: CAJ27
                          listName=invoice.invoice_supplier.responsability_regime_code)
        #DIAN 1.7.-2020: FAJ28
        #DIAN 1.7.-2020: CAJ28
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')

        #DIAN 1.7.-2020: FAJ29
        #DIAN 1.7.-2020: CAJ29
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_supplier.address.city.code)

        #DIAN 1.7.-2020: FAJ30
        #DIAN 1.7.-2020: CAJ30
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName', invoice.invoice_supplier.address.city.name)

        #DIAN 1.7.-2020: FAJ31
        #DIAN 1.7.-2020: CAJ31
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)

        #DIAN 1.7.-2020: FAJ32
        #DIAN 1.7.-2020: CAJ32
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)

        #DIAN 1.7.-2020: FAJ33,FAJ34
        #DIAN 1.7.-2020: CAJ33,CAJ34
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)

        #DIAN 1.7.-2020: FAJ35,FAJ36
        #DIAN 1.7.-2020: CAJ35,CAJ36
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)

        #DIAN 1.7.-2020: FAJ37,FAJ38
        #DIAN 1.7.-2020: CAJ37,CAJ38
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                          languageID='es')

        #DIAN 1.7.-2020: FAJ39
        #DIAN 1.7.-2020: CAJ39
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')

        #DIAN 1.7.-2020: CAJ40
        #DIAN 1.7.-2020: FAJ40
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          invoice.invoice_customer.tax_scheme.code)


        #DIAN 1.7.-2020: CAJ41
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          invoice.invoice_customer.tax_scheme.name)

        #DIAN 1.7.-2020: FAJ42
        #DIAN 1.7.-2020: CAJ42
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity')

        #DIAN 1.7.-2020: FAJ43
        #DIAN 1.7.-2020: CAJ43
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)

        #DIAN 1.7.-2020: FAJ44,FAJ45,FAJ46,FAJ47,FAJ48
        #DIAN 1.7.-2020: CAJ44,CAJ45,CAJ46,CAJ47,CAJ48
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          **supplier_company_id_attrs)

        #DIAN 1.7.-2020: FAJ49
        #DIAN 1.7.-2020: CAJ49
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme')

        #DIAN 1.7.-2020: FAJ50
        #DIAN 1.7.-2020: CAJ50
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme/cbc:ID',
                          invoice.invoice_ident_prefix)

        #DIAN 1.7.-2020: CAJ67
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:Contact')

        #DIAN 1.7.-2020: FAJ71
        #DIAN 1.7.-2020: CAJ71
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_supplier.email)


    def set_customer(fexml, invoice):
        fexml.placeholder_for('./cac:AccountingCustomerParty')
        fexml.set_element('./cac:AccountingCustomerParty/cbc:AdditionalAccountID',
                          invoice.invoice_customer.organization_code)
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID',
                          invoice.invoice_customer.ident)
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_customer.name)

        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation')
        customer_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        #DIAN 1.7.-2020: FAK25
        #DIAN 1.7.-2020: CAK25
        customer_company_id_attrs.update({'schemeID': invoice.invoice_customer.ident.dv,
                                          'schemeName': invoice.invoice_customer.ident.type_fiscal})

        #DIAN 1.7.-2020: FAK07
        #DIAN 1.7.-2020: CAK07
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address')

        #DIAN 1.7.-2020: FAK08
        #DIAN 1.7.-2020: CAK08
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: FAK09
        #DIAN 1.7.-2020: CAK09
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName', invoice.invoice_customer.address.city.name)

        #DIAN 1.7.-2020: FAK11
        #DIAN 1.7.-2020: CAK11
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)

        #DIAN 1.7.-2020: FAK12
        #DIAN 1.7.-2020: CAK12
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)

        #DIAN 1.7.-2020: CAK13, CAK14
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)

        #DIAN 1.7.-2020: CAK16
        #DIAN 1.7.-2020: FAK16
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)

        #DIAN 1.7.-2020: FAK17
        #DIAN 1.7.-2020: CAK17
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_customer.address.country.name,
                          #DIAN 1.7.-2020: FAK18
                          #DIAN 1.7.-2020: CAK18
                          languageID='es')

        #DIAN 1.7.-2020: FAK17,FAK19
        #DIAN 1.7.-2020: CAK19
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme')

        #DIAN 1.7.-2020: FAK17,FAK20
        #DIAN 1.7.-2020: CAK20
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)

        #DIAN 1.7.-2020: CAK21
        #DIAN 1.7.-2020: FAK21
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          #DIAN 1.7.-2020: CAK22, CAK23, CAK24, CAK25
                          **customer_company_id_attrs)

        #DIAN 1.7.-2020: CAK26
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          #DIAN 1.7.-2020: FAK26
                          invoice.invoice_customer.responsability_code,
                          #DIAN 1.7.-2020: FAK27
                          #DIAN 1.7.-2020: CAK27
                          listName=invoice.invoice_customer.responsability_regime_code)

        #DIAN 1.7.-2020: FAK28
        #DIAN 1.7.-2020: CAK28
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')

        #DIAN 1.7.-2020: FAK29
        #DIAN 1.7.-2020: CAK29
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_customer.address.city.code)

        #DIAN 1.7.-2020: FAK30
        #DIAN 1.7.-2020: CAK30
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName',
                          invoice.invoice_customer.address.city.name)

        #DIAN 1.7.-2020: FAK31
        #DIAN 1.7.-2020: CAK31
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)

        #DIAN 1.7.-2020: FAK32
        #DIAN 1.7.-2020: CAK32
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)

        #DIAN 1.7.-2020: FAK33
        #DIAN 1.7.-2020: CAK33
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine')

        #DIAN 1.7.-2020: FAK34
        #DIAN 1.7.-2020: CAK34
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)

        #DIAN 1.7.-2020: CAK35
        #DIAN 1.7.-2020: FAK35
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country')

        #DIAN 1.7.-2020: CAK36
        #DIAN 1.7.-2020: FAK36
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)

        #DIAN 1.7.-2020: CAK37
        #DIAN 1.7.-2020: FAK37
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name', invoice.invoice_customer.address.country.name)

        #DIAN 1.7.-2020: FAK38
        #DIAN 1.7.-2020: CAK38
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code,
                          languageID='es')

        #DIAN 1.7.-2020: CAK39
        #DIAN 1.7.-2020: FAK39
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')

        #DIAN 1.7.-2020: CAK40 Machete Construir Validación
        #DIAN 1.7.-2020: FAK40
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          invoice.invoice_customer.tax_scheme.code)

        #DIAN 1.7.-2020: FAK41
        #DIAN 1.7.-2020: CAK41 Machete Construir Validación
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          invoice.invoice_customer.tax_scheme.name)
        #DIAN 1.7.-2020: FAK42
        #DIAN 1.7.-2020: CAK42
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')

        #DIAN 1.7.-2020: FAK43
        #DIAN 1.7.-2020: CAK43
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)

        #DIAN 1.7.-2020: CAK44
        #DIAN 1.7.-2020: FAK44,FAK45,FAK46,FAK47,FAK48
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          **customer_company_id_attrs)

        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')

        #DIAN 1.7.-2020: FAK55
        #DIAN 1.7.-2020: CAK51, CAK55
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_customer.email)


    def set_payment_mean(fexml, invoice):
        payment_mean = invoice.invoice_payment_mean
        fexml.set_element('./cac:PaymentMeans/cbc:ID', payment_mean.id)
        fexml.set_element('./cac:PaymentMeans/cbc:PaymentMeansCode', payment_mean.code)
        fexml.set_element('./cac:PaymentMeans/cbc:PaymentDueDate', payment_mean.due_at.strftime('%Y-%m-%d'))
        fexml.set_element('./cac:PaymentMeans/cbc:PaymentID', payment_mean.payment_id)

    def set_element_amount_for(fexml, xml, xpath, amount):
        if not isinstance(amount, Amount):
            raise TypeError("amount not is Amount")

        xml.set_element(xpath, amount, currencyID=amount.currency.code)

    def set_element_amount(fexml, xpath, amount):
        if not isinstance(amount, Amount):
            raise TypeError("amount not is Amount")

        fexml.set_element(xpath, amount, currencyID=amount.currency.code)

    def set_legal_monetary(fexml, invoice):
        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:LineExtensionAmount',
                                 invoice.invoice_legal_monetary_total.line_extension_amount)

        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_exclusive_amount)

        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_inclusive_amount)

        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:ChargeTotalAmount',
                                invoice.invoice_legal_monetary_total.charge_total_amount)

        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:PayableAmount',
                                invoice.invoice_legal_monetary_total.payable_amount)


    def _set_invoice_document_reference(fexml, reference):
        fexml._do_set_billing_reference(reference, 'cac:InvoiceDocumentReference')

    def _set_credit_note_document_reference(fexml, reference):
        fexml._do_set_billing_reference(reference, 'cac:CreditNoteDocumentReference')

    def _set_debit_note_document_reference(fexml, reference):
        fexml._do_set_billing_reference(reference, 'cac:DebitNoteDocumentReference')

    def _do_set_billing_reference(fexml, reference, tag_document):
        fexml.set_element('./cac:BillingReference/%s/cbc:ID' %(tag_document),
                          reference.ident)
        fexml.set_element('./cac:BillingReference/cac:InvoiceDocumentReference/cbc:UUID',
                          reference.uuid,
                          schemeName='CUFE-SHA384')
        fexml.set_element('./cac:BillingReference/cac:InvoiceDocumentReference/cbc:IssueDate',
                          reference.date.strftime("%Y-%m-%d"))

    def set_billing_reference(fexml, invoice):
        reference = invoice.invoice_billing_reference
        if reference is None:
            return

        if isinstance(reference, DebitNoteDocumentReference):
            return fexml._set_debit_note_document_reference(reference)
        if isinstance(reference, CreditNoteDocumentReference):
            return fexml._set_credit_note_document_reference(reference)

        if isinstance(reference, InvoiceDocumentReference):
            return fexml._set_invoice_document_reference(reference)

    def set_invoice_totals(fexml, invoice):
        tax_amount_for = defaultdict(lambda: defaultdict(lambda: Amount(0.0)))
        percent_for = defaultdict(lambda: None)

        #requeridos para CUFE
        #tax_amount_for['01']['tax_amount'] = Amount(0.0)
        #tax_amount_for['01']['taxable_amount'] = Amount(0.0)
        #DIAN 1.7.-2020: FAS07 => Se debe construir estrategia para  su manejo
        #tax_amount_for['04']['tax_amount'] = 0.0
        #tax_amount_for['04']['taxable_amount'] = 0.0
        #tax_amount_for['03']['tax_amount'] = 0.0
        #tax_amount_for['03']['taxable_amount'] = 0.0

        total_tax_amount = Amount(0.0)

        for invoice_line in invoice.invoice_lines:
            for subtotal in invoice_line.tax.subtotals:
                if subtotal.scheme is not None:
                    tax_amount_for[subtotal.scheme.code]['tax_amount'] += subtotal.tax_amount
                    tax_amount_for[subtotal.scheme.code]['taxable_amount'] += invoice_line.taxable_amount

                    # MACHETE ojo InvoiceLine.tax pasar a Invoice
                    percent_for[subtotal.scheme.code] = subtotal.percent

                total_tax_amount += subtotal.tax_amount

        fexml.placeholder_for('./cac:TaxTotal')
        fexml.set_element_amount('./cac:TaxTotal/cbc:TaxAmount',
                                total_tax_amount)


        for index, item in enumerate(tax_amount_for.items()):
            cod_impuesto, amount_of = item
            next_append = index > 0

            #DIAN 1.7.-2020: FAS01
            line = fexml.fragment('./cac:TaxTotal', append=next_append)

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

    # abstract method
    def tag_document(fexml):
        return 'Invoice'

    # abstract method
    def tag_document_concilied(fexml):
        return 'Invoiced'

    def set_invoice_line_tax(fexml, line, invoice_line):
        fexml.set_element_amount_for(line,
                                     './cac:TaxTotal/cbc:TaxAmount',
                                     invoice_line.tax_amount)

        #DIAN 1.7.-2020: FAX05
        fexml.set_element_amount_for(line,
                                     './cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount',
                                     invoice_line.taxable_amount)

        for subtotal in invoice_line.tax.subtotals:
            line.set_element('./cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount', subtotal.tax_amount, currencyID='COP')

            if subtotal.percent is not None:
                line.set_element('./cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent', '%0.2f' % round(subtotal.percent, 2))

            if subtotal.scheme is not None:
                #DIAN 1.7.-2020: FAX15
                line.set_element('./cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID', subtotal.scheme.code)
                line.set_element('./cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name', subtotal.scheme.name)

    def set_invoice_lines(fexml, invoice):
        next_append = False
        for index, invoice_line in enumerate(invoice.invoice_lines):
            line = fexml.fragment('./cac:%sLine' % (fexml.tag_document()), append=next_append)
            next_append = True

            line.set_element('./cbc:ID', index + 1)
            line.set_element('./cbc:%sQuantity' % (fexml.tag_document_concilied()), invoice_line.quantity, unitCode = 'NAR')
            fexml.set_element_amount_for(line,
                                         './cbc:LineExtensionAmount',
                                         invoice_line.total_amount)

            if not isinstance(invoice_line.tax, TaxTotalOmit):
                fexml.set_invoice_line_tax(line, invoice_line)

            line.set_element('./cac:Item/cbc:Description', invoice_line.item.description)

            line.set_element('./cac:Item/cac:StandardItemIdentification/cbc:ID',
                             invoice_line.item.id,
                             schemeID=invoice_line.item.scheme_id,
                             schemeName=invoice_line.item.scheme_name,
                             schemeAgencyID=invoice_line.item.scheme_agency_id)

            line.set_element('./cac:Price/cbc:PriceAmount', invoice_line.price.amount, currencyID=invoice_line.price.amount.currency.code)
            #DIAN 1.7.-2020: FBB04
            line.set_element('./cac:Price/cbc:BaseQuantity',
                             invoice_line.price.quantity,
                             unitCode=invoice_line.quantity.code)

            for idx, charge in enumerate(invoice_line.allowance_charge):
                next_append_charge = idx > 0
                fexml.append_allowance_charge(line, index + 1, charge, append=next_append_charge)
                
    def set_allowance_charge(fexml, invoice):
        for idx, charge in enumerate(invoice.invoice_allowance_charge):
            next_append = idx > 0
            fexml.append_allowance_charge(fexml, idx + 1, charge, append=next_append)

    def append_allowance_charge(fexml, parent, idx, charge, append=False):
            line = parent.fragment('./cac:AllowanceCharge', append=append)
            #DIAN 1.7.-2020: FAQ02
            line.set_element('./cbc:ID', idx)
            #DIAN 1.7.-2020: FAQ03
            line.set_element('./cbc:ChargeIndicator', str(charge.charge_indicator).lower())
            if charge.reason:
                line.set_element('./cbc:AllowanceChargeReasonCode', charge.reason.code)
                line.set_element('./cbc:allowanceChargeReason', charge.reason.reason)
            line.set_element('./cbc:MultiplierFactorNumeric', str(round(charge.multiplier_factor_numeric, 2)))
            fexml.set_element_amount_for(line, './cbc:Amount', charge.amount)
            fexml.set_element_amount_for(line, './cbc:BaseAmount', charge.base_amount)
            
    def attach_invoice(fexml, invoice):
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""

        fexml.placeholder_for('./ext:UBLExtensions')
        fexml.set_element('./cbc:UBLVersionID', 'UBL 2.1')
        fexml.set_element('./cbc:CustomizationID', invoice.invoice_operation_type)
        fexml.placeholder_for('./cbc:ProfileID')
        fexml.placeholder_for('./cbc:ProfileExecutionID')
        fexml.set_element('./cbc:ID', invoice.invoice_ident)
        fexml.placeholder_for('./cbc:UUID')
        fexml.set_element('./cbc:DocumentCurrencyCode', 'COP')
        fexml.set_element('./cbc:IssueDate', invoice.invoice_issue.strftime('%Y-%m-%d'))
        #DIAN 1.7.-2020: FAD10
        fexml.set_element('./cbc:IssueTime', invoice.invoice_issue.strftime('%H:%M:%S-05:00'))
        fexml.set_element('./cbc:%sTypeCode' % (fexml.tag_document()),
                        invoice.invoice_type_code,
                        listAgencyID='195',
                        listAgencyName='No matching global declaration available for the validation root',
                        listURI='http://www.dian.gov.co')
        fexml.set_element('./cbc:LineCountNumeric', len(invoice.invoice_lines))
        fexml.set_element('./cac:%sPeriod/cbc:StartDate' % (fexml.tag_document()),
                          invoice.invoice_period_start.strftime('%Y-%m-%d'))

        fexml.set_element('./cac:%sPeriod/cbc:EndDate' % (fexml.tag_document()),
                          invoice.invoice_period_end.strftime('%Y-%m-%d'))

        fexml.customize(invoice)

        fexml.set_supplier(invoice)
        fexml.set_customer(invoice)
        fexml.set_legal_monetary(invoice)
        fexml.set_invoice_totals(invoice)
        fexml.set_invoice_lines(invoice)
        fexml.set_payment_mean(invoice)
        fexml.set_allowance_charge(invoice)
        fexml.set_billing_reference(invoice)

        return fexml

    def customize(fexml, invoice):
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""
