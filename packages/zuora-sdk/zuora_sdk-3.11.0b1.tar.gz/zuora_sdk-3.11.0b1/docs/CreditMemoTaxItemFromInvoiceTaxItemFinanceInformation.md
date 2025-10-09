# CreditMemoTaxItemFromInvoiceTaxItemFinanceInformation

Container for the finance information related to the source taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_tax_item_from_invoice_tax_item_finance_information import CreditMemoTaxItemFromInvoiceTaxItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoTaxItemFromInvoiceTaxItemFinanceInformation from a JSON string
credit_memo_tax_item_from_invoice_tax_item_finance_information_instance = CreditMemoTaxItemFromInvoiceTaxItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(CreditMemoTaxItemFromInvoiceTaxItemFinanceInformation.to_json())

# convert the object into a dict
credit_memo_tax_item_from_invoice_tax_item_finance_information_dict = credit_memo_tax_item_from_invoice_tax_item_finance_information_instance.to_dict()
# create an instance of CreditMemoTaxItemFromInvoiceTaxItemFinanceInformation from a dict
credit_memo_tax_item_from_invoice_tax_item_finance_information_from_dict = CreditMemoTaxItemFromInvoiceTaxItemFinanceInformation.from_dict(credit_memo_tax_item_from_invoice_tax_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


