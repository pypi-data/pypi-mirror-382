# TaxItemsFinanceInformation

Container for the finance information related to the taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounts_receivable_accounting_code** | **str** | The accounting code for accounts receivable.  | [optional] 
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.tax_items_finance_information import TaxItemsFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of TaxItemsFinanceInformation from a JSON string
tax_items_finance_information_instance = TaxItemsFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(TaxItemsFinanceInformation.to_json())

# convert the object into a dict
tax_items_finance_information_dict = tax_items_finance_information_instance.to_dict()
# create an instance of TaxItemsFinanceInformation from a dict
tax_items_finance_information_from_dict = TaxItemsFinanceInformation.from_dict(tax_items_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


