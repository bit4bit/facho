from .. import fe
from ..form import *
from datetime import datetime, date
from .attached_document import *

__all__ = ['DIANSupportDocumentXML']

class DIANSupportDocumentXML(fe.FeXML):
    """
    DianSupportDocumentXML mapea objeto form.Invoice a XML segun
    lo indicado para él Documento soporte en adquisiciones efectuadas con sujetos no obligados a expedir factura de venta o documento equivalente.
    """

    def __init__(self, invoice, tag_document = 'Invoice'):
        super().__init__(tag_document, 'http://www.dian.gov.co/contratos/facturaelectronica/v1')

        #DIAN 1.1.-2021: DSAB03
        #DIAN 1.1.-2021: NSAB03
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceControl')

        #DIAN 1.1.-2021: DSAB13
        #DIAN 1.1.-2021: NSAB13        
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:InvoiceSource')

        #DIAN 1.1.-2021: DSAB18
        #DIAN 1.1.-2021: NSAB18                
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareProvider')

        #DIAN 1.1.-2021: DSAB27
        #DIAN 1.1.-2021: NSAB27        
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:SoftwareSecurityCode')

        #DIAN 1.1.-2021: DSAB30 DSAB31
        #DIAN 1.1.-2021: NSAB30 NSAB31
        self.placeholder_for('./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/sts:DianExtensions/sts:AuthorizationProvider/sts:AuthorizationProviderID')
        
        #ZE02 se requiere existencia para firmar
        #DIAN 1.1.-2021: DSAA02 DSAB01
        #DIAN 1.1.-2021: NSAA02 NSAB01        
        ublextension = self.fragment('./ext:UBLExtensions/ext:UBLExtension', append=True)
        #DIAN 1.1.-2021: DSAB02
        #DIAN 1.1.-2021: NSAB02        
        extcontent = ublextension.find_or_create_element('/ext:UBLExtension/ext:ExtensionContent')
        self.attach_invoice(invoice)

    def set_supplier(fexml, invoice):
        #DIAN 1.1.-2021: DSAJ01       
        #DIAN 1.1.-2021: NSAB01
        fexml.placeholder_for('./cac:AccountingSupplierParty')

        #DIAN 1.1.-2021: DSAJ02
        #DIAN 1.1.-2021: NSAJ02
        fexml.set_element('./cac:AccountingSupplierParty/cbc:AdditionalAccountID',
                          invoice.invoice_supplier.organization_code)

        #DIAN 1.1.-2021: DSAJ07 DSAJ08
        #DIAN 1.1.-2021: NSAJ07 NSAJ08        
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address')

        #DIAN 1.1.-2021: DSAJ09
        #DIAN 1.1.-2021: NSAJ09        
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:ID',
                          invoice.invoice_supplier.address.city.code)

        #DIAN 1.1.-2021: DSAJ10
        #DIAN 1.1.-2021: NSAJ10        
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName',
                          invoice.invoice_supplier.address.city.name)

        #DIAN 1.1.-2021: DSAJ73
        #DIAN 1.1.-2021: NSAJ73        
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:PostalZone',
                          invoice.invoice_supplier.address.postalzone.code)

        #DIAN 1.1.-2021: DSAJ11
        #DIAN 1.1.-2021: NSAJ11 
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentity',
                          invoice.invoice_supplier.address.countrysubentity.name)

        #DIAN 1.1.-2021: DSAJ12
        #DIAN 1.1.-2021: NSAJ12
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CountrySubentityCode',
                          invoice.invoice_supplier.address.countrysubentity.code)

        #DIAN 1.1.-2021: DSAJ13 DSAJ14
        #DIAN 1.1.-2021: NSAJ13 NSAJ14
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:AddressLine/cbc:Line',
                          invoice.invoice_supplier.address.street)

        #DIAN 1.1.-2021: DSAJ15 DSAJ16
        #DIAN 1.1.-2021: NSAJ15 NSAJ16
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:IdentificationCode',
                          invoice.invoice_supplier.address.country.code)

        #DIAN 1.1.-2021: DSAJ17
        #DIAN 1.1.-2021: NSAJ17
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cac:Country/cbc:Name',
                          invoice.invoice_supplier.address.country.name,
                          #DIAN 1.1.-2021: DSAJ18
                          #DIAN 1.1.-2021: NSAJ18
                          languageID = 'es')


        supplier_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        supplier_company_id_attrs.update({'schemeID': invoice.invoice_supplier.ident.dv,
                                          'schemeName': invoice.invoice_supplier.ident.type_fiscal})

        #DIAN 1.1.-2021: DSAJ19
        #DIAN 1.1.-2021: NSAJ19
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme')

        #DIAN 1.1.-2021: DSAJ20
        #DIAN 1.1.-2021: NSAJ20
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_supplier.legal_name)

        #DIAN 1.1.-2021: DSAJ21
        #DIAN 1.1.-2021: NSAJ21
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_supplier.ident,
                          #DIAN 1.1.-2021: DSAJ22 DSAJ23 DSAJ24 DSAJ25
                          #DIAN 1.1.-2021: NSAJ22 NSAJ23 NSAJ24 NSAJ25
                          **supplier_company_id_attrs)

        #DIAN 1.1.-2021: DSAJ26
        #DIAN 1.1.-2021: NSAJ26        
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          invoice.invoice_supplier.responsability_code,
                          listName=invoice.invoice_supplier.responsability_regime_code)

        #DIAN 1.1.-2021: DSAJ39
        #DIAN 1.1.-2021: NSAJ39
        fexml.placeholder_for('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')

        #DIAN 1.1.-2021: DSAJ40
        #DIAN 1.1.-2021: NSAJ40
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          invoice.invoice_customer.tax_scheme.code)

        #DIAN 1.1.-2021: DSAJ41
        #DIAN 1.1.-2021: NSAJ41        
        fexml.set_element('./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          invoice.invoice_customer.tax_scheme.name)


    def set_customer(fexml, invoice):
        #DIAN 1.1.-2021: DSAK01
        #DIAN 1.1.-2021: NSAK01
        fexml.placeholder_for('./cac:AccountingCustomerParty')
        
        #DIAN 1.1.-2021: DSAK02
        #DIAN 1.1.-2021: NSAK02
        fexml.set_element('./cac:AccountingCustomerParty/cbc:AdditionalAccountID',
                          invoice.invoice_customer.organization_code)
        
        #DIAN 1.1.-2021: DSAK03
        #DIAN 1.1.-2021: NSAK03
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party')

        #DIAN 1.1.-2021: DSAK19
        #DIAN 1.1.-2021: NSAK19        
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme')

        #DIAN 1.1.-2021: DSAK20
        #DIAN 1.1.-2021: NSAK20
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
                          invoice.invoice_customer.legal_name)

        customer_company_id_attrs = fe.SCHEME_AGENCY_ATTRS.copy()
        customer_company_id_attrs.update({'schemeID': invoice.invoice_customer.ident.dv,
                                           'schemeName': invoice.invoice_customer.ident.type_fiscal})
        
        #DIAN 1.1.-2021: DSAK21
        #DIAN 1.1.-2021: NSAK21
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
                          invoice.invoice_customer.ident,
                          #DIAN 1.1.-2021: DSAK22 DSAK23 DSAK24 DSAK25
                          #DIAN 1.1.-2021: NSAK22 NSAK23 NSAK24 NSAK25
                          **customer_company_id_attrs)

        #DIAN 1.1.-2021: DSAK26
        #DIAN 1.1.-2021: NSAK26
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:TaxLevelCode',
                          invoice.invoice_customer.responsability_code)

        #DIAN 1.1.-2021: DSAK39
        #DIAN 1.1.-2021: NSAK39
        fexml.placeholder_for('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme')

        #DIAN 1.1.-2021: DSAK40
        #DIAN 1.1.-2021: NSAK40
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:ID',
                          invoice.invoice_customer.tax_scheme.code)

        #DIAN 1.1.-2021: DSAK41
        #DIAN 1.1.-2021: NSAK41
        fexml.set_element('./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name',
                          invoice.invoice_customer.tax_scheme.name)


    def set_payment_mean(fexml, invoice):
        payment_mean = invoice.invoice_payment_mean

        #DIAN 1.1.-2021: DSAN01 DSAN02
        #DIAN 1.1.-2021: NSAN02 NSAN02
        fexml.set_element('./cac:PaymentMeans/cbc:ID', payment_mean.id)

        #DIAN 1.1.-2021: DSAN03
        #DIAN 1.1.-2021: NSAN03
        fexml.set_element('./cac:PaymentMeans/cbc:PaymentMeansCode', payment_mean.code)

        #DIAN 1.1.-2021: DSAN04
        #DIAN 1.1.-2021: NSAN04        
        fexml.set_element('./cac:PaymentMeans/cbc:PaymentDueDate', payment_mean.due_at.strftime('%Y-%m-%d'))

        #DIAN 1.1.-2021: DSAN05
        #DIAN 1.1.-2021: NSAN05
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
        #DIAN 1.1.-2021: DSAU01 DSAU02 DSAU03
        #DIAN 1.1.-2021: NSAU01 NSAU02 NSAU03
        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:LineExtensionAmount',
                                 invoice.invoice_legal_monetary_total.line_extension_amount)

        #DIAN 1.1.-2021: DSAU04 DSAU05
        #DIAN 1.1.-2021: NSAU04 NSAU05
        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_exclusive_amount)

        #DIAN 1.1.-2021: DSAU06 DSAU07
        #DIAN 1.1.-2021: NSAU06 DSAU07
        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount',
                                invoice.invoice_legal_monetary_total.tax_inclusive_amount)

        #DIAN 1.1.-2021: DSAU10 DSAU11
        #DIAN 1.1.-2021: NSAU10 DSAU11
        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:ChargeTotalAmount',
                                invoice.invoice_legal_monetary_total.charge_total_amount)

        #DIAN 1.1.-2021: DSAU14 DSAU15
        #DIAN 1.1.-2021: NSAU14 DSAU15
        fexml.set_element_amount('./cac:LegalMonetaryTotal/cbc:PayableAmount',
                                invoice.invoice_legal_monetary_total.payable_amount)


    def _set_invoice_document_reference(fexml, reference):
        fexml._do_set_billing_reference(reference, 'cac:InvoiceDocumentReference')

    def _set_credit_note_document_reference(fexml, reference):
        fexml._do_set_billing_reference(reference, 'cac:CreditNoteDocumentReference')

    def _set_debit_note_document_reference(fexml, reference):
        fexml._do_set_billing_reference(reference, 'cac:DebitNoteDocumentReference')

    def _do_set_billing_reference(fexml, reference, tag_document):

        if tag_document == 'Invoice':
            schemeName = 'CUFE-SHA384'
        else:
            schemeName = 'CUDS-SHA384'
            
        fexml.set_element('./cac:BillingReference/%s/cbc:ID' %(tag_document),
                          reference.ident)
        fexml.set_element('./cac:BillingReference/cac:InvoiceDocumentReference/cbc:UUID',
                          reference.uuid,
                          schemeName=schemeName)
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

   # def set_discrepancy_response(fexml, invoice):
   #     reference = invoice.invoice_discrepancy_response
   #     if reference is None:
   #        return

        # if isinstance(reference, DebitNoteDocumentReference):
        #     return fexml._set_debit_note_document_reference(reference)
        # if isinstance(reference, CreditNoteDocumentReference):
        #     return fexml._set_credit_note_document_reference(reference)

        # if isinstance(reference, InvoiceDocumentReference):
        #     return fexml._set_invoice_document_reference(reference)

        # fexml.set_element('./cac:DiscrepancyResponse/cbc:ReferenceID',
        #                   reference.ident)
        # fexml.set_element('./cac:DiscrepancyResponse/cbc:ResponseCode:UUID',
        #                   '1')
        # fexml.set_element('./cac:DiscrepancyResponse/cbc:Description',
        #                   'Test')        

    def set_invoice_totals(fexml, invoice):
        tax_amount_for = defaultdict(lambda: defaultdict(lambda: Amount(0.0)))
        percent_for = defaultdict(lambda: None)

        total_tax_amount = Amount(0.0)

        for invoice_line in invoice.invoice_lines:
            for subtotal in invoice_line.tax.subtotals:
                if subtotal.scheme is not None:
                    tax_amount_for[subtotal.scheme.code]['tax_amount'] += subtotal.tax_amount
                    tax_amount_for[subtotal.scheme.code]['taxable_amount'] += invoice_line.taxable_amount

                    # MACHETE ojo InvoiceLine.tax pasar a Invoice
                    percent_for[subtotal.scheme.code] = subtotal.percent

                total_tax_amount += subtotal.tax_amount

        if total_tax_amount != Amount(0.0):
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
            line.set_element('/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name',
                    'IVA')
  
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

            period = line.fragment('./cac:InvoicePeriod')
            period.set_element('./cbc:StartDate',
                               datetime.now().strftime('%Y-%m-%d'))
            period.set_element('./cbc:DescriptionCode',
                               '1')
            period.set_element('./cbc:Description',
                               'Por operación')

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
        #fexml.set_discrepancy_response(invoice)        
        fexml.set_billing_reference(invoice)
     
        return fexml

    def customize(fexml, invoice):
        
        """adiciona etiquetas a FEXML y retorna FEXML
        en caso de fallar validacion retorna None"""
