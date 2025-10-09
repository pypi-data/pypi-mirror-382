# GetDebitMemoTaxItemFinanceInformation

Container for the finance information related to the taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 
**sales_tax_payable_accounting_code_type** | **str** | The type of the accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.get_debit_memo_tax_item_finance_information import GetDebitMemoTaxItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of GetDebitMemoTaxItemFinanceInformation from a JSON string
get_debit_memo_tax_item_finance_information_instance = GetDebitMemoTaxItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(GetDebitMemoTaxItemFinanceInformation.to_json())

# convert the object into a dict
get_debit_memo_tax_item_finance_information_dict = get_debit_memo_tax_item_finance_information_instance.to_dict()
# create an instance of GetDebitMemoTaxItemFinanceInformation from a dict
get_debit_memo_tax_item_finance_information_from_dict = GetDebitMemoTaxItemFinanceInformation.from_dict(get_debit_memo_tax_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


