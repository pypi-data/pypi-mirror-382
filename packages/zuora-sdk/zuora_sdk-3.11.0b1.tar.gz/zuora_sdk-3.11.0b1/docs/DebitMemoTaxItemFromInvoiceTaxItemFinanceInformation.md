# DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation

Container for the finance information related to the source taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_tax_item_from_invoice_tax_item_finance_information import DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation from a JSON string
debit_memo_tax_item_from_invoice_tax_item_finance_information_instance = DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation.to_json())

# convert the object into a dict
debit_memo_tax_item_from_invoice_tax_item_finance_information_dict = debit_memo_tax_item_from_invoice_tax_item_finance_information_instance.to_dict()
# create an instance of DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation from a dict
debit_memo_tax_item_from_invoice_tax_item_finance_information_from_dict = DebitMemoTaxItemFromInvoiceTaxItemFinanceInformation.from_dict(debit_memo_tax_item_from_invoice_tax_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


