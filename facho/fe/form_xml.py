from . import fe
from .form import *


class DIANInvoiceXML(fe.FeXML):
    """
    DianInvoiceXML mapea objeto form.Invoice a XML segun
    lo indicado para la facturacion electronica.
    """

    def __init__(self, invoice):
        super().__init__('Invoice', 'http://www.dian.gov.co/contratos/facturaelectronica/v1')
        self.placeholder_for('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent')

        # ZE02 se requiere existencia para firmar
        ublextension = self.fragment('/fe:Invoice/ext:UBLExtensions/ext:UBLExtension', append=True)
        extcontent = ublextension.find_or_create_element('/ext:UBLExtension/ext:ExtensionContent')
        self.attach_invoice(invoice)

    def set_supplier(fexml, invoice):
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty')
        #DIAN 1.7.-2020: FAJ02
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cbc:AdditionalAccountID',
                          invoice.invoice_supplier.organization_code)
        #DIAN 1.7.-2020: FAJ06
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_supplier.name)
        #DIAN 1.7.-2020: FAJ07
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address')
        #DIAN 1.7.-2020: FAJ08
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: FAJ09
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName',
                          invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: FAJ11
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)
        #DIAN 1.7.-2020: FAJ12
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: FAJ14
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)
        #DIAN 1.7.-2020: FAJ16
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)

        supplier_address_id_attrs = {'languageID' : 'es'}
        #DIAN 1.7.-2020: FAJ17
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                         #DIAN 1.7.-2020: FAJ18
                         **supplier_address_id_attrs)

        supplier_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        supplier_company_id_attrs.update({'schemeID': invoice.invoice_supplier.ident.dv,
                                          'schemeName': invoice.invoice_supplier.ident.type_fiscal})

        #DIAN 1.7.-2020: FAJ19
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme')
        #DIAN 1.7.-2020: FAJ20
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        #DIAN 1.7.-2020: FAJ21
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          #DIAN 1.7.-2020: FAJ22,FAJ23,FAJ24,FAJ25
                          **supplier_company_id_attrs)
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          #DIAN 1.7.-2020: FAJ26
                          invoice.invoice_supplier.responsability_code,
                          #DIAN 1.7.-2020: FAJ27
                          listName=invoice.invoice_supplier.responsability_regime_code)
        #DIAN 1.7.-2020: FAJ28
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')
        #DIAN 1.7.-2020: FAJ29
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_supplier.address.city.code)
        #DIAN 1.7.-2020: FAJ30
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName', invoice.invoice_supplier.address.city.name)
        #DIAN 1.7.-2020: FAJ31
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)
        #DIAN 1.7.-2020: FAJ32
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)
        #DIAN 1.7.-2020: FAJ33,FAJ34
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)
        #DIAN 1.7.-2020: FAJ35,FAJ36
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)
        supplier_address_id_attrs = {'languageID' : 'es'}
        #DIAN 1.7.-2020: FAJ37,FAJ38
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                          **supplier_address_id_attrs)
        #DIAN 1.7.-2020: FAJ39
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')

        #DIAN 1.7.-2020: FAJ42
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: FAJ43
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)
        #DIAN 1.7.-2020: FAJ44,FAJ45,FAJ46,FAJ47,FAJ48
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          **supplier_company_id_attrs)
        #DIAN 1.7.-2020: FAJ49
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme')
        #DIAN 1.7.-2020: FAJ50
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cac:CorporateRegistrationScheme/cbc:ID',
                          'SETP')
        fexml.placeholder_for('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact')
        #DIAN 1.7.-2020: FAJ71
        fexml.set_element('/fe:Invoice/cac:AccountingSupplierParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_supplier.email)


    def set_customer(fexml, invoice):
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty')
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cbc:AdditionalAccountID',
                          invoice.invoice_customer.organization_code)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID',
                          invoice.invoice_customer.ident)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name',
                          invoice.invoice_customer.name)

        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation')
        customer_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        #DIAN 1.7.-2020: FAK25
        customer_company_id_attrs.update({'schemeID': invoice.invoice_customer.ident.dv,
                                          'schemeName': invoice.invoice_customer.ident.type_fiscal})
        #DIAN 1.7.-2020: FAK07
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address')
        #DIAN 1.7.-2020: FAK08
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: FAK09
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName', invoice.invoice_customer.address.city.name)
        #DIAN 1.7.-2020: FAK11
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)
        #DIAN 1.7.-2020: FAK12
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)
        #DIAN 1.7.-2020: FAK16
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)
        customer_address_id_attrs = {'languageID' : 'es'}
        #DIAN 1.7.-2020: FAK17
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_customer.address.country.name,
                         #DIAN 1.7.-2020: FAK18
                         **customer_address_id_attrs)
        #DIAN 1.7.-2020: FAK17,FAK19
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme')
        #DIAN 1.7.-2020: FAK17,FAK20
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        #DIAN 1.7.-2020: FAK21
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          **customer_company_id_attrs)
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          #DIAN 1.7.-2020: FAK26
                          invoice.invoice_customer.responsability_code,
                          #DIAN 1.7.-2020: FAK27
                          listName=invoice.invoice_customer.responsability_regime_code)
        #DIAN 1.7.-2020: FAK28
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress')
        #DIAN 1.7.-2020: FAK29
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:ID',
                          invoice.invoice_customer.address.city.code)
        #DIAN 1.7.-2020: FAK30
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CityName',
                          invoice.invoice_customer.address.city.name)
        #DIAN 1.7.-2020: FAK31
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentity',
                          invoice.invoice_customer.address.countrysubentity.name)
        #DIAN 1.7.-2020: FAK32
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:CountrySubentityCode',
                          invoice.invoice_customer.address.countrysubentity.code)
        #DIAN 1.7.-2020: FAK33
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine')
        #DIAN 1.7.-2020: FAK34
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:AddressLine/cbc:Line',
                          invoice.invoice_customer.address.street)
        #DIAN 1.7.-2020: FAK35
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country')
        #DIAN 1.7.-2020: FAK36
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code)
        #DIAN 1.7.-2020: FAK37
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:Name', invoice.invoice_customer.address.country.name)
        #DIAN 1.7.-2020: FAK38
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:RegistrationAddress/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_customer.address.country.code,
                          **customer_address_id_attrs)
        #DIAN 1.7.-2020: FAK39
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')
        #DIAN 1.7.-2020: FAK40 Machete Construir Validación
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          'ZY')
        #DIAN 1.7.-2020: FAK41 Machete Construir Validación
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          'No causa')
        #DIAN 1.7.-2020: FAK42
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: FAK43
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)
        #DIAN 1.7.-2020: FAK44,FAK45,FAK46,FAK47,FAK48
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          **customer_company_id_attrs)
        #DIAN 1.7.-2020: FAK51
        fexml.placeholder_for('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity')
        #DIAN 1.7.-2020: FAK55
        fexml.set_element('/fe:Invoice/cac:AccountingCustomerParty/cac:Party/cac:Contact/cbc:ElectronicMail',
                          invoice.invoice_customer.email)

    def set_payment_mean(fexml, invoice):
        payment_mean = invoice.invoice_payment_mean
        fexml.set_element('/fe:Invoice/cac:PaymentMeans/cbc:ID', payment_mean.id)
        fexml.set_element('/fe:Invoice/cac:PaymentMeans/cbc:PaymentMeansCode', payment_mean.code)
        fexml.set_element('/fe:Invoice/cac:PaymentMeans/cbc:PaymentDueDate', payment_mean.due_at.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:Invoice/cac:PaymentMeans/cbc:PaymentID', payment_mean.payment_id)

    def set_element_amount_for(fexml, xml, xpath, amount):
        if not isinstance(amount, Amount):
            raise TypeError("amount not is Amount")

        xml.set_element(xpath, amount, currencyID=amount.currency.code)

    def set_element_amount(fexml, xpath, amount):
        if not isinstance(amount, Amount):
            raise TypeError("amount not is Amount")

        fexml.set_element(xpath, amount, currencyID=amount.currency.code)

    def set_legal_monetary(fexml, invoice):
        fexml.set_element_amount('/fe:Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount',
                                 invoice.invoice_legal_monetary_total.line_extension_amount)

        fexml.set_element_amount('/fe:Invoice/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_exclusive_amount)

        fexml.set_element_amount('/fe:Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_inclusive_amount)

        fexml.set_element_amount('/fe:Invoice/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount',
                                invoice.invoice_legal_monetary_total.charge_total_amount)

        fexml.set_element_amount('/fe:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount',
                                invoice.invoice_legal_monetary_total.payable_amount)


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
                # MACHETE ojo InvoiceLine.tax pasar a Invoice
                percent_for[subtotal.tax_scheme_ident] = subtotal.percent

        fexml.placeholder_for('/fe:Invoice/cac:TaxTotal')
        fexml.set_element_amount('/fe:Invoice/cac:TaxTotal/cbc:TaxAmount',
                                total_tax_amount)


        for index, item in enumerate(tax_amount_for.items()):
            cod_impuesto, amount_of = item
            next_append = index > 0

            #DIAN 1.7.-2020: FAS01
            line = fexml.fragment('/fe:Invoice/cac:TaxTotal', append=next_append)

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
            line = fexml.fragment('/fe:Invoice/cac:InvoiceLine', append=next_append)
            next_append = True

            line.set_element('/cac:InvoiceLine/cbc:ID', index + 1)
            line.set_element('/cac:InvoiceLine/cbc:InvoicedQuantity', invoice_line.quantity, unitCode = 'NAR')
            fexml.set_element_amount_for(line,
                                         '/cac:InvoiceLine/cbc:LineExtensionAmount',
                                         invoice_line.total_amount)
            fexml.set_element_amount_for(line,
                                         '/cac:InvoiceLine/cac:TaxTotal/cbc:TaxAmount',
                                         invoice_line.tax_amount)

            #condition_price = line.fragment('/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice')
            #condition_price.set_element('/cac:AlternativeConditionPrice/cbc:PriceAmount', invoice_line.price.amount, currencyID='COP')
            #condition_price.set_element('/cac:AlternativeConditionPrice/cbc:PriceTypeCode', invoice_line.price.type_code)
            #condition_price.set_element('/cac:AlternativeConditionPrice/cbc:PriceType', invoice_line.price.type)

            for subtotal in invoice_line.tax.subtotals:
                fexml.set_element_amount_for(line,
                                             '/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount',
                                             subtotal.taxable_amount)
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount', subtotal.tax_amount, currencyID='COP')
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent', subtotal.percent)
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID', subtotal.tax_scheme_ident)
                line.set_element('/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name', subtotal.tax_scheme_name)
            line.set_element('/cac:InvoiceLine/cac:Item/cbc:Description', invoice_line.item.description)
            # TODO
            line.set_element('/cac:InvoiceLine/cac:Item/cac:StandardItemIdentification/cbc:ID', invoice_line.item.id)
            line.set_element('/cac:InvoiceLine/cac:Price/cbc:PriceAmount', invoice_line.price.amount, currencyID="COP")
            #DIAN 1.7.-2020: FBB04
            line.set_element('/cac:InvoiceLine/cac:Price/cbc:BaseQuantity', invoice_line.price.amount)

    def attach_invoice(fexml, invoice):
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""

        fexml.placeholder_for('/fe:Invoice/ext:UBLExtensions')
        fexml.set_element('/fe:Invoice/cbc:UBLVersionID', 'UBL 2.1')
        fexml.set_element('/fe:Invoice/cbc:CustomizationID', invoice.invoice_operation_type)
        fexml.placeholder_for('/fe:Invoice/cbc:ProfileID')
        fexml.placeholder_for('/fe:Invoice/cbc:ProfileExecutionID')
        fexml.set_element('/fe:Invoice/cbc:ID', invoice.invoice_ident)
        fexml.placeholder_for('/fe:Invoice/cbc:UUID')
        fexml.set_element('/fe:Invoice/cbc:DocumentCurrencyCode', 'COP')
        fexml.set_element('/fe:Invoice/cbc:IssueDate', invoice.invoice_issue.strftime('%Y-%m-%d'))
        #DIAN 1.7.-2020: FAD10
        fexml.set_element('/fe:Invoice/cbc:IssueTime', invoice.invoice_issue.strftime('%H:%M:%S-05:00'))
        fexml.set_element('/fe:Invoice/cbc:InvoiceTypeCode', codelist.TipoDocumento.by_name('Factura de Venta Nacional')['code'],
                          listAgencyID='195',
                          listAgencyName='No matching global declaration available for the validation root',
                          listURI='http://www.dian.gov.co')
        fexml.set_element('/fe:Invoice/cbc:LineCountNumeric', len(invoice.invoice_lines))
        fexml.set_element('/fe:Invoice/cac:InvoicePeriod/cbc:StartDate', invoice.invoice_period_start.strftime('%Y-%m-%d'))
        fexml.set_element('/fe:Invoice/cac:InvoicePeriod/cbc:EndDate', invoice.invoice_period_end.strftime('%Y-%m-%d'))

        fexml.set_supplier(invoice)
        fexml.set_customer(invoice)
        fexml.set_legal_monetary(invoice)
        fexml.set_invoice_totals(invoice)
        fexml.set_invoice_lines(invoice)
        fexml.set_payment_mean(invoice)

        return fexml


def DIANWrite(xml, filename):
    document = xml.tostring(xml_declaration=True, encoding='UTF-8')
    with open(filename, 'w') as f:
        f.write(document)

        
def DIANWriteSigned(xml, filename, private_key, passphrase, use_cache_policy=False):
    document = xml.tostring(xml_declaration=True, encoding='UTF-8')
    signer = fe.DianXMLExtensionSigner(private_key, passphrase=passphrase, mockpolicy=use_cache_policy)
    with open(filename, 'w') as f:
        f.write(signer.sign_xml_string(document))
